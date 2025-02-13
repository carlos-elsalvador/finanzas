from finanzas import *

# Este programa tiene dos partes. En la primera se leen y se dibujan los datos de las aportaciones realizadas a la cooperativa ACOFINGES,
# descargados de la web como archivo CSV. En la segunda parte, con esos mismos datos se calcula el interés compuesto. 
# ACOFINGES aplica la fórmula del interés compuesto tomando un mes como unidad de tiempo, interés mensual. 
# Fecha 11/02/2025

# LECTURA DE DATOS
#Leemos los datos de los archivos correspondientes a las cuentas de : APORTACIONES:    'acofingesAPO.csv'
# (1) Se define ruta; (2) Se lee archivo CSV; y (3) Se limita a las columnas 'Fecha', 'Depósito' y 'Saldo'

main_dir              = '/home/carlos/workbenchPython/finanzas/datos/'
ap                    = pd.read_csv(main_dir+'acofingesAPO.csv', parse_dates=['Fecha'], dayfirst=True, decimal=".", thousands=',')
ap                    = ap[['Fecha', 'Depósito', 'Saldo']]

# PREPARACION DE DATOS
# Convertir con manejo de errores, errors="coerce" convierte valores inválidos en NaN, evitando fallos.
ap['Depósito']        = pd.to_numeric(ap['Depósito'], errors='coerce').fillna(0)  # Convierte, pone NaN en errores
ap['Saldo']           = pd.to_numeric(ap['Saldo'], errors='coerce').fillna(0)


# ***PARTE I***

#Depositos y SaldosANUALes
anual_deposito       = ap.groupby(ap['Fecha'].dt.year).sum()['Depósito']
anual_saldo          = ap.groupby(ap['Fecha'].dt.year).last()['Saldo']

# Para cada caso, los totales se calculan de manera diferente. En la Series 'Depósito' se suman los depositos anuales. Para 
# la Series 'Saldo' se toma en cuenta que: se tiene una Series, no un DataFrame. Si anual_saldo fuera un DataFrame, necesitaríamos dos índices (iloc[fila, columna]). Pero al ser una Series, solo necesita un índice (iloc[fila]).

total_deposito       = anual_deposito.sum()
total_saldo          = anual_saldo.iloc[-1]

#Titulos
titulo_deposito      = 'Depósitos ACOFINGES, '+str(anual_deposito.index[0])+'-'+str(anual_deposito.index[-1])+' (Total:'+str(total_deposito)+')'

titulo_saldo         = 'Saldos ACOFINGES, '+str(anual_saldo.index[0])+'-'+str(anual_saldo.index[-1])+' (Total:'+str(total_saldo)+')'

#PLOT depositos
plot_barras(anual_deposito, apilado=True, rotulos=['Year','Depósito [US$]',titulo_deposito])
#PLOT saldos
plot_barras(anual_saldo, apilado=True, rotulos=['Year','Saldo [US$]',titulo_saldo])

#PARTE II
# CALCULO DE LA RENTABILIDAD ANUAL. Se debe tener en cuenta que la unidad de tiempo en el fondo de aportaciones es MENSUAL
# Es decir, el interés compuesto debe tener en cuenta la peculiaridad del mes de enero, donde el Saldo del año anterior
# debe sumarse a las aportaciones realizadas dentro de ese mes. Ese requiere de un tratamiento especial sobre los datos.
# Ese tratamiento especial se resume en tener un unico valor de deposito para cada mes de cada ejercicio. Como ya se dijo,
# el mes de enero es especial pues hay que sumarle el saldo del ano anterior. El tratamiento se resume en 4 pasos:
# (1) Usar groupby para agrupar datos por mes y año. Luego, aplicar función filtrar_enero para conservar solo la última fila de enero.
ap                    = ap.groupby(ap['Fecha'].dt.year).apply(filtrar_enero).reset_index(drop=True)

# (2) Identificar las filas correspondientes al mes de enero para asignar a los depósitos el valor del saldo
ene                   = ap['Fecha'].dt.month == 1
ap.loc[ene,'Depósito']= ap.loc[ene, 'Saldo']
# (3) set index
ap                    = ap.set_index('Fecha')                   
# (4) se agrupan sumando las operaciones de los restantes meses.
ap_mes                = ap.groupby(pd.Grouper(freq='M')).sum()

# La cooperativa ACOFINGES calcula el interes mensual. Para seleccionar el ejercicio se realizan los siguientes pasos
# (1) Se selecciona un ejercicio (año); (2) Se crea mascara y (3) Se realizan los cálculos del interés compuesto. 

# Intereses. En mi caso a partir de 2019 en aportaciones. El interés de las aportaciones es mensual (/12).
intereses_anual         = {2019:7, 2020:5.5, 2021:2.0, 2022:5, 2023:4.42, 2024:4.5}

ejercicio             = 2024
interes_mes           = intereses_anual.get(ejercicio)/12
mask                  = (ap_mes.index.year == ejercicio)
year                  = ap_mes.loc[mask]

#
datos                 = ejercicio_anual(year, interes_mes)

resultado             = datos['resultado'].sum().round(2)
Saldo                 = datos['Depósito'].sum()

print('Ejercicio %d: Saldo %.2f, Interés %.2f: Resultado %.2f' % (ejercicio, Saldo, intereses_anual.get(ejercicio), resultado))

