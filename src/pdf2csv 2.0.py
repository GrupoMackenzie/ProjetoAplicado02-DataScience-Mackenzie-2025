# pdf2csv 2.0.py

# Gera datasets/serasa.csv a partir dos PDFs

# INADIMPLENTES_MI - Número de pessoas inadimplentes em milhões
# VMPP - Valor médio por pessoa inadimplente em reais (R$)
# DIVIDAS_MI - Quantidade total de dívidas em milhões
# VMCD - Valor médio de cada dívida em reais (R$)
# VTDD_BI - Valor total das dívidas em bilhões de reais (R$ bi)
# VMAF - Valor médio dos acordos fechados em reais (R$)
# DESCONTOS_BI - Descontos concedidos em bilhões de reais (R$ bi)
# Formato nome do PDF: SERASA Mapa da Inadimplencia <Mês> <Ano>.pdf

"""
Pessoal imagens dos plots salvas na pasta figures, csv na pasta datasets,
e carregamento na pasta /datasets/mapas_serasa como ja estava ajustado pelo Diogo
"""

from pathlib import Path
import re
import unicodedata
import pandas as pd
import pdfplumber

# -------------------------------------------------------
# Bl.1 Configuração de caminhos
# -------------------------------------------------------
PDF_DIR = Path("datasets/mapas_serasa")   # onde estão os PDFs
OUTPUT_CSV = Path("datasets/serasa.csv")  # saída desejada


# -------------------------------------------------------
# Bl.2 Normalização
# -------------------------------------------------------
def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

def norm_line(s: str) -> str:
    if s is None:
        return ""
    s = strip_accents(s.upper())
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def parse_brl(value_str: str):
    """
    Converter strings em Float o que não fiz no projeto aplicado 1 :)
    """
    if not value_str:
        return None
    s = re.sub(r"[^\d\.,]", "", value_str)
    if not s:
        return None

    # Diogo um caso bizarro: várias vírgulas e nenhum ponto (ex.: '5,837,49')
    if s.count(",") > 1 and "." not in s:
        parts = s.split(",")
        s = "".join(parts[:-1]) + "," + parts[-1]

    if "," in s and "." in s:
        # Para padronizar milhar: 5.496,69
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:

        s = s.replace(",", ".")
    elif "." in s:

        pass

    try:
        return float(s)
    except ValueError:
        return None


# -------------------------------------------------------
# Bl.3 Extração dos textos
# -------------------------------------------------------
def extract_text_pdfplumber(pdf_path: Path) -> str:
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            texts.append(t)
    return "\n".join(texts)


# -------------------------------------------------------
# Bl.3.1 Extração dos indicadores que vamos usar
# -------------------------------------------------------
def extract_metrics_from_pdf(pdf_path: Path) -> dict:

    text = extract_text_pdfplumber(pdf_path)
    lines = text.splitlines()
    norms = [norm_line(l) for l in lines]

    pairs = re.findall(r"([\d\.,]+)\s*mi\s*R\$\s*([\d\.,]+)", text, flags=re.IGNORECASE)

    inad_mi = div_mi = vmpp = vmcd = None
    if len(pairs) >= 2:
        inad_mi = parse_brl(pairs[0][0])
        vmpp    = parse_brl(pairs[0][1])
        div_mi  = parse_brl(pairs[1][0])
        vmcd    = parse_brl(pairs[1][1])

    vtdd = vmaf = descontos = None

    for i, n in enumerate(norms):
        if "VALOR TOTAL DAS DIVIDAS" in n:
            for j in range(i - 5, i + 2):
                if 0 <= j < len(lines):
                    m = re.search(r"R\$\s*([\d\.,]+)\s*bi", lines[j], flags=re.IGNORECASE)
                    if m:
                        vtdd = parse_brl(m.group(1))
                        break
            if vtdd is not None:
                break

    for i, n in enumerate(norms):
        if "VALOR MEDIO DOS" in n and any(
            "ACORDOS FECHADOS" in norms[k]
            for k in range(i, min(len(norms), i + 5))
        ):
            for j in range(i - 10, i + 1):
                if 0 <= j < len(lines):

                    m = re.search(r"R\$\s*([\d\.,]+)(?![^\n]*bilh)", lines[j], flags=re.IGNORECASE)
                    if m:
                        vmaf = parse_brl(m.group(1))
                        break
            if vmaf is not None:
                break

    for i, n in enumerate(norms):
        if "DESCONTOS CONCEDIDOS" in n:
            for j in range(i - 5, i + 3):
                if 0 <= j < len(lines):
                    m = re.search(r"R\$\s*([\d\.,]+)[^\n]*bilh", lines[j], flags=re.IGNORECASE)
                    if m:
                        descontos = parse_brl(m.group(1))
                        break
            if descontos is not None:
                break

    return {
        "INADIMPLENTES_MI": inad_mi,
        "VMPP": vmpp,
        "DIVIDAS_MI": div_mi,
        "VMCD": vmcd,
        "VTDD_BI": vtdd,
        "VMAF": vmaf,
        "DESCONTOS_BI": descontos,
    }


# -------------------------------------------------------
# Bl.4 PERIODO, usei o nome dos pdf
# -------------------------------------------------------
def normalize_month_name(name: str) -> str:
    name = strip_accents(name.lower().strip())
    return name

def period_from_filename(pdf_path: Path) -> str:

    name = pdf_path.stem
    m = re.search(r"([A-Za-zçÇ]+)\s+(\d{4})$", name)
    if not m:
        return name

    month_raw, year = m.group(1), m.group(2)
    month_norm = normalize_month_name(month_raw)

    abbr_map = {
        "janeiro": "jan", "fevereiro": "fev", "marco": "mar",
        "abril": "abr", "maio": "mai", "junho": "jun", "julho": "jul",
        "agosto": "ago", "setembro": "set", "outubro": "out",
        "novembro": "nov", "dezembro": "dez",
    }

    abbr = abbr_map.get(month_norm, month_norm[:3])
    return f"{abbr}/{year[-2:]}"


# -------------------------------------------------------
# Bl.5 Criação do CSV
# -------------------------------------------------------
def periodo_sort_key(p: str):

    if not isinstance(p, str) or "/" not in p:
        return (9999, 99)
    mes_abbr, yy = p.split("/")
    mes_order = {
        "jan": 1, "fev": 2, "mar": 3, "abr": 4,
        "mai": 5, "jun": 6, "jul": 7, "ago": 8,
        "set": 9, "out": 10, "nov": 11, "dez": 12,
    }
    m = mes_order.get(mes_abbr.lower(), 99)
    try:
        y = 2000 + int(yy)
    except ValueError:
        y = 9999
    return (y, m)

def build_dataset():
    if not PDF_DIR.exists():
        raise FileNotFoundError(f"Pasta dos PDFs não encontrada: {PDF_DIR}")

    rows = []
    for pdf_file in sorted(PDF_DIR.glob("*.pdf")):
        print(f"[INFO] Processando {pdf_file.name}...")
        metrics = extract_metrics_from_pdf(pdf_file)
        metrics["PERIODO"] = period_from_filename(pdf_file)
        rows.append(metrics)

    if not rows:
        print("[AVISO] Não foram encontrados os PDF.")
        return

    cols = [
        "PERIODO",
        "INADIMPLENTES_MI",
        "VMPP",
        "DIVIDAS_MI",
        "VMCD",
        "VTDD_BI",
        "VMAF",
        "DESCONTOS_BI",
    ]

    df = pd.DataFrame(rows, columns=cols)

    # Ajustei para tipo numérico nas colunas de métrica
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Para ordenar pelo PERIODO (ano/mês)
    df = df.sort_values(by="PERIODO", key=lambda s: s.map(periodo_sort_key))

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"[OK] CSV gerado em: {OUTPUT_CSV.resolve()}")


if __name__ == "__main__":
    build_dataset()