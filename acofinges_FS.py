from finanzas import *

# Este programa tiene tres partes. En la primera se leen y se dibujan los datos del fondo solidario de la cooperativa ACOFINGES,
# descargados de la web como archivo CSV. En la segunda parte, con esos mismos datos se calcula el interés compuesto y 
# se compara con la rentabilidad del fondo. En la tercera parte se realiza una simulación con depósitos a realizar en un nuevo año
# Observación: Existe una pequeña diferencia entre el rendimiento de la cooperativa (parte I) y el calculado con la fórmula (parte II).
# Como no se dispone de información de cómo ACOFINGES aplica la fórmula del interés compuesto se ha hecho la suposición de que su año tiene 
# una duración de 360 dias. 
# Fecha 23/01/2025

# ***PARTE I***

# LECTURA DE DATOS
# Se leen los datos de los archivos correspondientes a la cuenta del Fondo Solidario de la cooperativa ACOFINGES
# (1) Se define ruta; (2) Se lee archivo CSV; y (3) Se cambia la columna Fecha a índice
main_dir              = '/home/carlos/workbenchPython/finanzas/datos/'
fs                    = pd.read_csv(main_dir+'FS.csv', parse_dates=['Fecha'], dayfirst=True, decimal=".", thousands=',')
# Convertir con manejo de errores, errors="coerce" convierte valores inválidos en NaN, evitando fallos.
fs['Depósito']        = pd.to_numeric(fs['Depósito'], errors='coerce').fillna(0)  # Convierte, pone NaN en errores
fs['Saldo']           = pd.to_numeric(fs['Saldo'], errors='coerce').fillna(0)  # Convierte, pone NaN en errores
#set index
fs                    = fs.set_index('Fecha')                   

# PREPARACION DE DATOS
# Se identifica y se separa la última operación de c/año, correspondiente al rendimiento anual ('abono') del fondo [CAP-FSR-YEAR]
# y a el saldo total de ese mismo año.
fsr                   = fs.groupby(pd.Grouper(level=0,freq = 'A')).tail(1)

# Se separan aportaciones propias ('Aportación') de las generadas por el fondo ('Rendimiento'). Para lo cual:
# (1) se crea una nueva columna ['Rendimiento'], correspondiente a los rendimientos anuales acumulandos, y 
# (2) Se obtiene la diferencia entre el Saldo (que incluye los rendimientos) y los rendimientos anuales acumulados.
fsr['Rendimiento']    = fsr['Depósito'].cumsum(axis = 0)
fsr['Aportacion']     = fsr['Saldo']-fsr['Rendimiento']

#Para simplificar la representación gráfica se reducen los datos a las aportaciones y a los rendimientos anuales.
fsr                   = fsr[['Aportacion','Rendimiento']]

#Se cambia el formato del índice de fecha a únicamente año
fsr.index             = fsr.index.year

#PLOT. Resultados anuales del fondo
plot_barras(fsr, apilado=True, rotulos=['Year','US$','Aportaciones y redimiento del Fondo Solidario, ACOFINGES'])


# ***PARTE II***
# Se calcula y se comparan los rendimientos, el abonado por ACOFINGES contra el calculado con fórmula interés compuesto. 
# El último saldo de cada 31 de diciembre se convierte en el deposito del 1 de enero del año siguiente. Para lo cual: 
# (1) Se cambia la fecha de 31 de diciembre a 1 de enero del siguiente año y 
# (2) Se cambia el saldo a deposito.
# (3) También, se agrega una nueva columna, correspondiente al número de días en un año sujeto a la tasa de interés anual

# 1/
fs.index              = fs.index.map(cambiar_fecha)
# 2/
mask                  = (fs.index.month == 1) & (fs.index.day == 1) 
fs.loc[mask, ['Depósito', 'Saldo']] = fs.loc[mask, ['Saldo', 'Depósito']].values
# 3/
fs['dias']            = 360-fs.index.dayofyear

# Se establecen algunas variables:
# El inicio de cada año como el 1 de enero y el final como el 30 de diciembre.
fecha_ini             =  [datetime(k,1,1)   for k in fsr.index]
fecha_fin             =  [datetime(k,12,30) for k in fsr.index]
# Se utilizan los intereses publicados por ACOFINGES
intereses_anual       =  {2022:6.77, 2023:6.5, 2024:6.38} #Interés diario 

# Mediane un lazo for, se calcula el interés compuesto anual, excluyendo el 31 de diciembre
resultados            = []
for k, year in enumerate(fsr.index):
    interes           = intereses_anual.get(year)/365 #interes diario
    mask              = (fs.index >= fecha_ini[k]) & (fs.index <= fecha_fin[k])
    anual             = fs.loc[mask].copy()
    # Aplicar la función fila por fila
    anual['compuesto']= anual.apply(lambda row: compound_interest(row['Depósito'], interes, row['dias']), axis=1).round(2)
    anual['resultado']= anual['compuesto']-anual['Depósito']
    resultados.append(anual['resultado'].sum().round(2))

# Se extraen los rendimientos anuales calculados por ACOFIGES
acofinge              = fs.loc[(fs.index.month == 1) & (fs.index.day == 1)]['Saldo'].values.tolist()
#year
year                  = fs.loc[(fs.index.month == 1) & (fs.index.day == 1)].index.year.values.tolist()
# Se crea nuevo dataframe con ambos resultados
compara              = pd.DataFrame({'Año':year,'ACOFINGES':acofinge,'CALCULADO':resultados})
# Set index
compara              = compara.set_index('Año')                   
#PLOT
plot_barras(compara, apilado=False, rotulos=['Year','US$','Comparación ACOFINGES vs Interés Compuesto Calculado'])

#***PARTE III***
#Se simulará la rentabilidad del fondo para nuevas inversiones durante un año. Para lo cual se toman los siguientes pasos:
# (1) Se establece como valor inicial el último dato del año anterior. (2) Se define un valor de interés anual y 
# (3) se crean dos listas una correspondiente a los nuevos depósitos mensuales (depo) y la otra a su respectiva fecha (fecha). 
# La lista fecha correspondera al mismo tiempo con el indice del nuevo DataFrame
simula                = fs.tail(1)
new_interes           = 6.1/365
depo_list             = []
fecha_list            = []
# Los elementos de la lista de depósitos están formados por el par campo/dato, {'campo':dato}.
# Por otra parte los elementos de la lista de fechas estan formados por strings con formato de fecha, YYYY/MM/DD.
for i in range(2,13):
    depo_list.append({'Depósito': 850})
    fecha_list.append('2025-'+ str(i)+'-25')
# Con el par de listas se crea temporalmente un DataFrame, luego se concatena con el DataFrame que contiene el saldo anual inicial
new_rows              = pd.DataFrame(depo_list, index=pd.to_datetime(fecha_list))
simula                = pd.concat([simula, new_rows])
# Con el nuevo DataFrame que contiene los 'depósitos' simulados se ejecutan los mismos pasos que la PARTE II.
simula['dias']        = 360-simula.index.dayofyear
    # Aplicar la función fila por fila
simula['compuesto']   = simula.apply(lambda row: compound_interest(row['Depósito'], new_interes, row['dias']), axis=1).round(2)
simula['resultado']   = simula['compuesto']-simula['Depósito']

# Se agrega el resultado de la simulacion a la parte I   
# FALTA CORREGIR: (1) EJE DE TIEMPO, AGREGAR A INDEX 1 ANYO y (2) aportaciones y (3) redondear a dos decimales
aporta                = simula.iloc[1:,1].sum() + fsr.iloc[-1,0]
resulta               = simula.iloc[:,-1].sum() + fsr.iloc[-1,-1]
fsr.loc[len(fsr)]     = [aporta, resulta.round(2)]

# Change the last index cell to 2025
fsr.index = fsr.index[:-1].tolist() + [2025]
print(fsr)

#PLOT
plot_barras(fsr, apilado=True, rotulos=['Year','US$','Aportación/Redimiento FS-ACOFINGES y simulacion del último año'])


# OTROS AGRUPAMIENTOS
# Se realizan agrupamientos, acumulados mediante suma, mensuales (mes) y anuales (anu)
#mes             = fs.groupby(pd.Grouper(freq='M')).sum()
#anu             = fs.groupby(pd.Grouper(freq='Y')).sum()


