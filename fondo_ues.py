import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

main_dir       = '/home/carlos/Descargas/workbenchPython/eie_pandas/demografia/'
df             = pd.read_csv(main_dir+'cotiza.csv', parse_dates=['Fecha'], dayfirst=True)  

# Set index
df.set_index('Fecha', inplace = True)

# 
# Se suman los valores de inyecciones (MWh) mediante: agrupamiento diario(D), mensual (ME) y anual (YE).
df_M       = df.groupby(pd.Grouper(freq='M')).sum()
df_Y       = df.groupby(pd.Grouper(freq='Y')).sum()

#PLOT
fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(10,6))
fig.suptitle('Universidad de El Salvador, Salaries 1994-2024')

#Variables a usar
fechas = [dt.datetime(1994, 6, 1), dt.datetime(1998, 5, 1), dt.datetime(2004, 8, 1), dt.datetime(2017, 9, 1), dt.datetime(2024, 12, 31)]
colores = ['red','green','blue', 'gray']
posX    = [0.07, 0.18,0.38,0.8]
teXt    = ['INST','PUI','PUII','PUIII']   
    
# Anual
ax1.plot(df_Y.index, 0.1*df_Y['Cotiza'], '*', color='green', linestyle='solid')
ax1.set_ylabel('Anual Salary [Thousand US$]')
ax1.grid()

#plot lineas verticales ax1
for k, fecha in enumerate(fechas[:-1]):
    print(k,fecha)
    ax1.axvline(fecha, color="black", linestyle='dashed',linewidth=0.5)
    ax1.axvspan(fechas[k], fechas[k+1], alpha=0.25, color=colores[k])
    ax1.text(posX[k], 0.75, teXt[k], horizontalalignment='center',  verticalalignment='center', transform=ax1.transAxes)
#
#Mensual
ax2.plot(df_M.index, 100*df_M['Cotiza'], '.', color='red', linestyle='dashed')
ax2.set_ylabel('Monthly Salary [US$]')
ax2.grid()

#plot lineas verticales ax2  (ya no es necesario definir fechas y colores)
for k, fecha in enumerate(fechas[:-1]):
    print(k,fecha)
    ax2.axvline(fecha, color="black", linestyle='dashed',linewidth=0.5)
    ax2.axvspan(fechas[k], fechas[k+1], alpha=0.15, color=colores[k])
    ax2.text(posX[k], 0.75, teXt[k], horizontalalignment='center',  verticalalignment='center', transform=ax2.transAxes)

plt.xlabel('Year')
plt.show()

#PLOT. Grafico de Barras.
# Anual
plt.figure(figsize=(10, 6))
plt.bar(df_Y.index.year, 0.1*df_Y['Cotiza'], color='green')
plt.ylabel('Anual Salary [Thousand US$]')
plt.title('Universidad de El Salvador, Salaries 1994-2024')
plt.grid()
plt.xlabel('Year')
plt.show()



#Datos estadisitcos
anual          = df.groupby(df.index.year)['Cotiza'].agg(['sum', 'mean', 'max', 'count'])#.unstack(level=2)
print(anual)
print('TOTAL COTIZACIONES:',anual['sum'].sum().round(2))

