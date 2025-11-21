# EDA + modelo preditivo de VTDD usando datasets/serasa.csv

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# Bl.1 Configurações básicas

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "datasets" / "serasa.csv"
FIG_DIR = BASE_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True, parents=True)

plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["axes.grid"] = True

# Bl.2 Funções auxiliares de período

MESES_FULL = {
    "jan": "Janeiro",
    "fev": "Fevereiro",
    "mar": "Março",
    "abr": "Abril",
    "mai": "Maio",
    "jun": "Junho",
    "jul": "Julho",
    "ago": "Agosto",
    "set": "Setembro",
    "out": "Outubro",
    "nov": "Novembro",
    "dez": "Dezembro",
}


def periodo_sort_key(p: str):
    """Transformei 'out/24' em (2024, 10) para uma melhor ordenação temporal."""
    if not isinstance(p, str) or "/" not in p:
        return (9999, 99)
    mes, yy = p.split("/")
    mes = mes.lower()
    mapa = {
        "jan": 1, "fev": 2, "mar": 3, "abr": 4,
        "mai": 5, "jun": 6, "jul": 7, "ago": 8,
        "set": 9, "out": 10, "nov": 11, "dez": 12,
    }
    m = mapa.get(mes, 99)
    try:
        y = 2000 + int(yy)
    except ValueError:
        y = 9999
    return (y, m)


def periodo_full_label(p: str) -> str:

    if not isinstance(p, str) or "/" not in p:
        return p
    mes_abbr, yy = p.split("/")
    mes_nome = MESES_FULL.get(mes_abbr.lower(), mes_abbr)
    try:
        ano = 2000 + int(yy)
    except ValueError:
        ano = yy
    return f"{mes_nome} {ano}"



# Bl.3 Carregamento e tratamento inicial

def load_data():
    df = pd.read_csv(DATA_PATH)

    num_cols = [
        "INADIMPLENTES_MI",
        "VMPP",
        "DIVIDAS_MI",
        "VMCD",
        "VTDD_BI",
        "VMAF",
        "DESCONTOS_BI",
    ]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 3.1 Ordenar por período
    df = df.sort_values("PERIODO", key=lambda s: s.map(periodo_sort_key)).reset_index(drop=True)

    df["t"] = np.arange(len(df))

    df["PERIODO_FULL"] = df["PERIODO"].apply(periodo_full_label)

    return df



# Bl.4 EDA: estatísticas, correlações, gráficos, tabelas

def eda_basic_stats(df: pd.DataFrame):
    print("\n=== Estatísticas descritivas gerais ===")
    print(df.describe(include="all"))

    print("\n=== Estatísticas focadas em VTDD_BI e INADIMPLENTES_MI ===")
    print(df[["VTDD_BI", "INADIMPLENTES_MI"]].describe())


def eda_correlations(df: pd.DataFrame):
    corr = df[[
        "INADIMPLENTES_MI",
        "VMPP",
        "DIVIDAS_MI",
        "VMCD",
        "VTDD_BI",
        "VMAF",
        "DESCONTOS_BI",
    ]].corr()

    plt.figure()
    sns.heatmap(corr, annot=True, fmt=".2f")
    plt.title("Matriz de Correlação - Indicadores Serasa")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "correlacao_indicadores.png")
    plt.close()

    print("\n=== Matriz de correlação ===")
    print(corr)


# Bl.5 Figuras:
def plot_inadimplentes_time_series(df: pd.DataFrame):
    """Gabriel: Figura: Evolução de Inadimplência no Brasil."""
    plt.figure()
    plt.plot(df["PERIODO_FULL"], df["INADIMPLENTES_MI"], marker="o")
    plt.xlabel("Período")
    plt.ylabel("Inadimplentes (milhões)")
    plt.title("Evolução da Inadimplência no Brasil")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "inadimplentes_serie_temporal.png")
    plt.close()


def plot_vmpp_time_series(df: pd.DataFrame):
    """Gabriel: Figura: Evolução do Valor Médio por Pessoa (VMPP)."""
    plt.figure()
    plt.plot(df["PERIODO_FULL"], df["VMPP"], marker="o")
    plt.xlabel("Período")
    plt.ylabel("VMPP (R$)")
    plt.title("Valor Médio por Pessoa (VMPP) – Série Temporal")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "vmpp_serie_temporal.png")
    plt.close()


def plot_dividas_time_series(df: pd.DataFrame):
    """Gabriel: Figura: Variação da quantidade total de dívidas (DIVIDAS_MI)."""
    plt.figure()
    plt.plot(df["PERIODO_FULL"], df["DIVIDAS_MI"], marker="o")
    plt.xlabel("Período")
    plt.ylabel("Quantidade de Dívidas (milhões)")
    plt.title("Variação das Dívidas Brasileiras ao Longo do Tempo")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "dividas_serie_temporal.png")
    plt.close()


def plot_vmcd_time_series(df: pd.DataFrame):
    """Gabriel: Figura: Evolução do Valor Médio de Cada Dívida (VMCD)."""
    plt.figure()
    plt.plot(df["PERIODO_FULL"], df["VMCD"], marker="o")
    plt.xlabel("Período")
    plt.ylabel("VMCD (R$)")
    plt.title("Valor Médio de Cada Dívida (VMCD) – Série Temporal")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "vmcd_serie_temporal.png")
    plt.close()


def plot_vtdd_time_series(df: pd.DataFrame):
    """Gabriel: Figura: Total de dívidas em reais (R$)."""
    plt.figure()
    plt.plot(df["PERIODO_FULL"], df["VTDD_BI"], marker="o")
    plt.xlabel("Período")
    plt.ylabel("VTDD (R$ bilhões)")
    plt.title("Valor Total das Dívidas (VTDD) – Série Temporal")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "vtdd_serie_temporal.png")
    plt.close()


# Bl5.1 Plots de Histogramas e boxplots
def plot_histograms_boxplots(df: pd.DataFrame):

    plt.figure()
    plt.hist(df["VTDD_BI"], bins=5)
    plt.xlabel("VTDD (R$ bilhões)")
    plt.ylabel("Frequência")
    plt.title("Histograma do Valor Total das Dívidas (VTDD)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "vtdd_histograma.png")
    plt.close()

    plt.figure()
    sns.boxplot(x=df["VTDD_BI"])
    plt.xlabel("VTDD (R$ bilhões)")
    plt.title("Boxplot do Valor Total das Dívidas (VTDD)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "vtdd_boxplot.png")
    plt.close()

    plt.figure()
    plt.hist(df["INADIMPLENTES_MI"], bins=5)
    plt.xlabel("Inadimplentes (milhões)")
    plt.ylabel("Frequência")
    plt.title("Histograma do Número de Inadimplentes")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "inadimplentes_histograma.png")
    plt.close()


# Gabriel -- Pizza
def build_inadimplentes_table(df: pd.DataFrame) -> pd.DataFrame:

    linhas = []
    total_inad = df["INADIMPLENTES_MI"].sum()

    for _, row in df.iterrows():
        per = row["PERIODO"]
        mes_abbr, yy = per.split("/")
        mes_nome = MESES_FULL.get(mes_abbr.lower(), mes_abbr)
        ano = 2000 + int(yy)
        qtd = row["INADIMPLENTES_MI"]
        pct = 100 * qtd / total_inad

        linhas.append({
            "Mês": mes_nome,
            "Ano": ano,
            "% Total (no período)": round(pct, 2),
            "Qtd. Total (mi)": round(qtd, 2),
        })

    tab = pd.DataFrame(linhas)
    total_row = {
        "Mês": "Total",
        "Ano": "",
        "% Total (no período)": round(tab["% Total (no período)"].sum(), 2),
        "Qtd. Total (mi)": round(total_inad, 1),
    }
    tab = pd.concat([tab, pd.DataFrame([total_row])], ignore_index=True)

    print("\n=== Tabela - Número de Inadimplentes (estilo Tabela 1) ===")
    print(tab.to_string(index=False))

    out_path = BASE_DIR / "datasets" / "tabela_inadimplentes.csv"
    out_path.parent.mkdir(exist_ok=True, parents=True)
    tab.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\nTabela de inadimplentes salva em: {out_path}")

    return tab


def plot_inadimplentes_pie(df: pd.DataFrame):
    """
    Gabriel esse é o Gráfico de pizza: distribuição dos inadimplentes por período atualizado que vc pediu.
    """
    labels = df["PERIODO_FULL"].tolist()
    sizes = df["INADIMPLENTES_MI"].tolist()

    plt.figure(figsize=(8, 8))
    plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90
    )
    plt.title("Distribuição dos Inadimplentes por Período")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "inadimplentes_pizza.png")
    plt.close()


# -------------------------------------------------------------------
# BL.6 Modelo preditivo de VTDD (série temporal) + métricas + Tabela atenção as legendas
# -------------------------------------------------------------------
def train_vtdd_model(df: pd.DataFrame):

    df = df.sort_values("t").reset_index(drop=True)

    X = df[["t"]].values
    y = df["VTDD_BI"].values

    n = len(df)
    n_train = int(n * 0.7)  # 70% treino, 30% teste

    X_train, X_test = X[:n_train], X[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Previsão no conjunto de teste das métricas
    y_pred_test = model.predict(X_test)

    r2 = r2_score(y_test, y_pred_test)
    # sklearn
    rmse = mean_squared_error(y_test, y_pred_test) ** 0.5

    print("\n=== Métricas de desempenho do modelo (conjunto de teste) ===")
    print(f"R² (coeficiente de determinação): {r2:.4f}")
    print(f"RMSE (erro quadrático médio, em R$ bilhões): {rmse:.2f}")

    # Previsão em TODO o histórico """(para VTDD_PRED em Tabela 2)"""
    y_pred_hist = model.predict(X)

    # Reajusta em todos os dados para projetar próximos 5 meses (pedido do Gabriel)
    model_full = LinearRegression()
    model_full.fit(X, y)

    last_t = df["t"].iloc[-1]
    future_steps = 5
    future_t = np.arange(last_t + 1, last_t + 1 + future_steps).reshape(-1, 1)
    future_pred = model_full.predict(future_t)

    # Monta tabela
    tabela2 = build_forecast_table(df, y_pred_hist, future_pred)

    out_path = BASE_DIR / "datasets" / "tabela_vtdd_previsao.csv"
    tabela2.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\nTabela de previsão VTDD salva em: {out_path}")

    # Gráfico histórico + previsão
    plot_forecast(df, future_pred)

    return model, tabela2


def build_forecast_table(df: pd.DataFrame,
                         y_pred_hist: np.ndarray,
                         future_pred: np.ndarray) -> pd.DataFrame:

    hist = pd.DataFrame({
        "PERIODO": df["PERIODO"],
        "VTDD_REAL (R$ B)": df["VTDD_BI"],
        "VTDD_PRED (R$ B)": np.round(y_pred_hist, 2),
        "VTDD_PREVISTA (R$ B)": np.nan,
    })

    future_periods = ["ago/25", "set/25", "out/25", "nov/25", "dez/25"]
    future = pd.DataFrame({
        "PERIODO": future_periods,
        "VTDD_REAL (R$ B)": [np.nan] * len(future_periods),
        "VTDD_PRED (R$ B)": [np.nan] * len(future_periods),
        "VTDD_PREVISTA (R$ B)": np.round(future_pred, 2),
    })

    tabela2 = pd.concat([hist, future], ignore_index=True)
    print("\n=== Tabela 2 - VTDD histórico, previsto e projeções ===")
    print(tabela2.to_string(index=False))
    return tabela2


def plot_forecast(df: pd.DataFrame, future_pred: np.ndarray):

    x_hist = df["PERIODO"].tolist()                # ex: ['out/24', ..., 'jul/25']
    x_future = ["ago/25", "set/25", "out/25", "nov/25", "dez/25"]

    y_hist = df["VTDD_BI"].values
    y_future = future_pred

    def full_label(p):
        return periodo_full_label(p)

    labels_hist_full = [full_label(p) for p in x_hist]
    labels_future_full = [full_label(p) for p in x_future]
    labels_all = labels_hist_full + labels_future_full

    # Índices numéricos no eixo x (Atenção)
    x_hist_idx = np.arange(len(x_hist))
    x_future_idx = np.arange(len(x_hist), len(x_hist) + len(x_future))

    plt.figure(figsize=(10, 4))

    # linha histórica
    plt.plot(x_hist_idx, y_hist, marker="o", label="Histórico")

    # linha de previsão tracejada nesse caso
    plt.plot(x_future_idx, y_future, marker="o", linestyle="--", label="Previsão")

    # rótulos do eixo X com meses
    plt.xticks(
        ticks=np.arange(len(labels_all)),
        labels=labels_all,
        rotation=45
    )

    plt.xlabel("Período")
    plt.ylabel("Valor Total das Dívidas (R$ bilhões)")
    plt.title("Previsão de Dívidas para os Próximos 5 Meses – Brasil (em Bilhões de R$)")
    plt.legend()
    plt.tight_layout()

    for x, y in zip(x_hist_idx, y_hist):
        plt.text(x, y + 2, f"{round(y):.0f}B", ha="center", va="bottom", fontsize=8)

    for x, y in zip(x_future_idx, y_future):
        plt.text(x, y + 2, f"{round(y):.0f}B", ha="center", va="bottom", fontsize=8)

    plt.savefig(FIG_DIR / "vtdd_previsao_proximos_5_meses.png")
    plt.close()

def main():
    print(f"Lendo dados de: {DATA_PATH}")
    df = load_data()

    # Tratamento / EDA básica
    eda_basic_stats(df)
    eda_correlations(df)

    # Séries temporais principais (substituem Figuras 2–5 no documento """Gabriel ou Ana""")
    plot_inadimplentes_time_series(df)
    plot_vmpp_time_series(df)
    plot_dividas_time_series(df)
    plot_vmcd_time_series(df)
    plot_vtdd_time_series(df)

    # Histogramas / boxplots
    plot_histograms_boxplots(df)

    # Tabela 1 - Inadimplentes + pizza
    build_inadimplentes_table(df)
    plot_inadimplentes_pie(df)

    # Modelo preditivo + métricas de acurácia + Tabela 2 + Figura de previsão
    train_vtdd_model(df)


if __name__ == "__main__":
    main()

"""AMÉM"""