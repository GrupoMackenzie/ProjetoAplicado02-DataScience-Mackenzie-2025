import pdfplumber
import pandas as pd
import glob

#VMAF - Valor Médio dos Acordos Fechados em reais
#DESC_CONC - Descontos Concedidos em bilhões
#INADIMPLENTES - Em milhões
#VMPP - Valor médio por pessoa em reais
#DIVIDAS - Quantidade de dívidas em milhões
#VMCD - Valor médio de cada dívida em reais
#VTDD - Valor total das dívidas em bilhões

columns = ['VMAF', 'DESC_CONC', 'INADIMPLENTES', 'VMPP', 'DIVIDAS', 'VMCD', 'VTDD']

files = glob.glob("../datasets/mapas_serasa/*.pdf")

output = {}

for file in files:
    print(file)
    with pdfplumber.open(file) as pdf:
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
        filename = file.split()
        filename = filename[len(filename)-2:len(filename)]
        filename = filename[0] + " " + filename[1][:len(filename[1])-4]
        output[filename] = values

df = pd.DataFrame(output.values(), columns=columns, index=output.keys())
print(df)

#df.to_csv("../datasets/serasa.csv")