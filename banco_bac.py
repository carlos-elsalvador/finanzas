from CarlosAnalytic_pandas import *
#Fecha Transaccion,Fecha Aplicada,Hora,Transaccion,Referencia,Cargo,Abono,Saldo,Canal,Categoria

main_dir       = '/home/carlos/Descargas/workbenchPython/eie_pandas/demografia/'
#df             = pd.read_csv(main_dir+'bac.csv', parse_dates=['Fecha Transaccion', 'Fecha Aplicada'], dayfirst=True)  
df             = pd.read_csv(main_dir+'BAC_corr.csv', parse_dates=['Fecha Transaccion', 'Fecha Aplicada'], dayfirst=True)  
#Tipos de Transacción: Cargo o Abono
#Cargos, Tran   =['Compra: UBER', 'SELECTOS',  'CLARO', 'CAESS', 'ANDA', 'IVON', 'AG SAN LUIS', 'FARMACIA', 'DENTISTA', 'Digicel'], 'Cargo'
Abonos, Tran   =['UES', 'PLANILLA', 'UES: BONO', 'UES: AGUINALDO', 'UES: CONCAPAN'],'Abono'
df             = df[df['Transaccion'].str.contains(Abonos[0], na=False)]

#df             = pd_eliminasimbolos(df,Tran)
Total          = df[Tran].sum().round()
anual          = df.groupby(df['Fecha Transaccion'].dt.year)[Tran].agg(['sum', 'mean', 'max', 'count'])#.unstack(level=2)
print(anual)

plt.plot(df['Fecha Transaccion'], df[Tran], 'ko-', linewidth=2.5)
plt.title('PERIODO  US$'+str(Total))
plt.grid()
plt.ylabel('US$')
plt.show()

anual['sum'].plot(kind='bar',color='b')
plt.title('PERIODO  US$'+str(Total))
plt.grid()
plt.ylabel('US$')
plt.show()


# df             = pd_eliminasimbolos(df,Tran)
# CN  = pd.DataFrame()
# for index, k in enumerate(Abonos[2:4]):
#     df1             = df[df['Transaccion'].str.contains(k, na=False)]
#     anual          = df1.groupby(df1['Fecha Transaccion'].dt.year)[Tran].agg(['sum'])#.unstack(level=2)
#     CN[index] = anual['sum'] 
# print(CN)
# CN.plot.bar(stacked=True)
# plt.grid()
# plt.ylabel('US$')
# plt.show()
