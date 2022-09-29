import pandas as pd
import xlsxwriter

df = pd.DataFrame()

for i in range(1,15):
    excel = pd.read_excel('B10808006_林亭毅_爬蟲_作業一_{}.xlsx'.format(i))
    df = pd.concat([df , excel], ignore_index=True)
    

df = df.drop(['Unnamed: 0'], axis=1)
    
df.to_excel('./B10808006_林亭毅_爬蟲_作業一.xlsx', engine = 'xlsxwriter')