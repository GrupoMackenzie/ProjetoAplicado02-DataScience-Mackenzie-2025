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

with pdfplumber.open("../datasets/SERASA Mapa da Inadimplencia Maio.pdf") as pdf:
    for page in range(len(pdf.pages)):
        match page:
            case 3:
                values = []
                page_text = pdf.pages[page].extract_text().split()
                for index in range(len(page_text)):
                    match page_text[index]:
                        case 'R$':
                            values.append(page_text[index+1])
                        case 'mi':
                            values.append(page_text[index-1])

                for column, index in zip(columns, values):
                    df[column] = [index]

            case 5:
                page_text = pdf.pages[page].extract_text_simple().split()
                #print(page_text)]


print(df.head())