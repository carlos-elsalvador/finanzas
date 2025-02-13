import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- FUNCIONES AUXILIARES ---
def cambiar_fecha(fecha: pd.Timestamp) -> pd.Timestamp:
    """Si la fecha es 31 de diciembre, la cambia al 1 de enero del año siguiente."""
    return fecha + pd.DateOffset(days=1) if fecha.month == 12 and fecha.day == 31 else fecha

def compound_interest(principal: float, rate: float, time: int) -> float:
    """Calcula el interés compuesto."""
    return principal * ((1 + rate / 100) ** time)

def plot_barras(df: pd.DataFrame, apilado=True, etiquetas=('X', 'Y', 'Título')):
    """Genera un gráfico de barras a partir de un DataFrame."""
    ax = df.plot(kind='bar', stacked=apilado, color=['green', 'red', 'blue', 'yellow'], rot=0)
    ax.legend(loc='upper left')
    ax.set_xlabel(etiquetas[0])
    ax.set_ylabel(etiquetas[1])
    ax.set_title(etiquetas[2])
    ax.grid()
    plt.show()

# --- CARGA Y PREPARACIÓN DE DATOS ---
main_dir = '/home/carlos/Descargas/workbenchPython/eie_pandas/'
fs = pd.read_csv(f'{main_dir}FS.csv', parse_dates=['Fecha'], dayfirst=True, decimal=".", thousands=',')
fs.set_index('Fecha', inplace=True)

# Identificar la última operación de cada año
fsr = fs.groupby(pd.Grouper(level=0, freq='A')).tail(1)
fsr['Rendimiento'] = fsr['Depósito'].cumsum()
fsr['Aportacion'] = fsr['Saldo'] - fsr['Rendimiento']
fsr = fsr[['Aportacion', 'Rendimiento']]
fsr.index = fsr.index.year
plot_barras(fsr, True, ('Año', 'US$', 'Aportaciones y Rendimiento'))

# --- CÁLCULO DE INTERÉS COMPUESTO ---
fs.index = fs.index.to_series().apply(cambiar_fecha)
mask = (fs.index.month == 1) & (fs.index.day == 1)
fs.loc[mask, ['Depósito', 'Saldo']] = fs.loc[mask, ['Saldo', 'Depósito']].values
fs['dias'] = 360 - fs.index.dayofyear

fecha_ini = [datetime(y, 1, 1) for y in fsr.index]
fecha_fin = [datetime(y, 12, 30) for y in fsr.index]
interes = np.array([6.77, 6.5, 6.38]) / 365

resultados = [
    fs.loc[(fs.index >= fecha_ini[i]) & (fs.index <= fecha_fin[i]), 'Depósito']
    .mul((1 + interes[i]) ** fs.loc[(fs.index >= fecha_ini[i]) & (fs.index <= fecha_fin[i]), 'dias'])
    .sub(fs.loc[(fs.index >= fecha_ini[i]) & (fs.index <= fecha_fin[i]), 'Depósito'])
    .sum().round(2)
    for i in range(len(fsr.index))
]

acofinge = fs.loc[mask, 'Saldo'].values.tolist()
years = fs.loc[mask].index.year.tolist()
compara = pd.DataFrame({'Año': years, 'ACOFINGES': acofinge, 'CALCULADO': resultados}).set_index('Año')
plot_barras(compara, False, ('Año', 'US$', 'Comparación ACOFINGES vs Calculado'))

# --- SIMULACIÓN PARA UN NUEVO AÑO ---
simula = fs.tail(1)
new_interest = 6.1 / 365
simula = pd.concat([
    simula,
    pd.DataFrame(
        {'Depósito': 850}, index=pd.date_range("2025-02-25", "2025-12-25", freq='MS')
    )
])

simula['dias'] = 360 - simula.index.dayofyear
simula['compuesto'] = simula['Depósito'] * ((1 + new_interest) ** simula['dias'])
simula['resultado'] = simula['compuesto'] - simula['Depósito']

aporta = simula.iloc[1:, 1].sum() + fsr.iloc[-1, 0]
resulta = simula.iloc[:, -1].sum() + fsr.iloc[-1, -1]
fsr.loc[2025] = [aporta, resulta.round(2)]
plot_barras(fsr, True, ('Año', 'US$', 'Aportación y Rendimiento con Simulación'))

