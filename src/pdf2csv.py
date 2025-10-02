import pdfplumber
import pandas as pd

#VMAF - Valor Médio dos Acordos Fechados em reais
#DESC_CONC - Descontos Concedidos em bilhões
#INADIMPLENTES - Em milhões
#VMPP - Valor médio por pessoa em reais
#DIVIDAS - Quantidade de dívidas em milhões
#VMCD - Valor médio de cada dívida em reais
#VTDD - Valor total das dívidas em bilhões

columns = ['VMAF', 'DESC_CONC', 'INADIMPLENTES', 'VMPP', 'DIVIDAS', 'VMCD', 'VTDD']

df = pd.DataFrame({x: [] for x in columns})

with pdfplumber.open("../datasets/SERASA Mapa da Inadimplencia Julho 2025.pdf") as pdf:
    for page in range(len(pdf.pages)):
        match page:
            case 3:
                indexes = [5, 20, 22, 25, 42, 45, 57]
                page_text = pdf.pages[page].extract_text().split()
                for column, index in zip(columns, indexes):
                    df[column] = [page_text[index]]

            case 5:
                page_text = pdf.pages[page].extract_text_simple().split()
                #print(page_text)


print(df.head())