# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import xlrd
import os
from datetime import date,datetime,time,timedelta
import seaborn as sns
import scipy.stats
import numpy as np

def cambiar_fecha(fecha):
    """
    Función para cambiar fecha. Se cambia la fecha de la última operación del año, 31/12 al primer día del siguiente 01/01.
    fecha: Fecha de la última operacion de un año dado, 31/12. 

    Devuelve: cambio de fecha, 01/01.
    
    Descripción: Al descargar los datos de los saldos del fondo solidario de la cooperativa ACOFINGES se observa que 
    la última operación del año corresponde al 'abono' de la bonificación del fondo, se depositan los intereses generados
    por las aportaciones a lo largo del año, incluyendo el saldo del año anterior. Sin embargo, para el cálculo del interés
    compuesto de la totalidad de la serie se requiere que ese 'abono' sea desplazado al 1 de enero del año siguiente. 
    """
    if fecha.month == 12 and fecha.day == 31:
        return fecha + pd.DateOffset(days=1)
    return fecha


def compound_interest(principal, rate, time):
    """
    Función para calcular el interés compuesto. 
    
    Entradas:
            principal:  Aportación realizada en una fecha dada al fondo, 'Abono'. 
            rate:       Tipo de interés. Se introduce en forma porcentual, para luego convertirlo en decimal (dividiendo por 100)
            time:       Unidad de tiempo. Pueden ser dias, meses o años.
    
    Devuelve: 
                        El interés compuesto de la entrada
    Raises:
            ValueError: Si los valores de principal o time son negativos.
            TypeError:  Si las entradas no son numéricas.

    Ultima actualización:        8/2/2025          
    Por:                 cemc (c)
    """
      
    # Validación de tipos
    if not all(isinstance(x, (int, float)) for x in [principal, rate, time]):
        raise TypeError("Los valores de principal, rate y time deben ser números.")
    
    # Validación de valores negativos
    if principal < 0:
        raise ValueError("El principal no puede ser negativo.")
    if time < 0:
        raise ValueError("El tiempo no puede ser negativo.")

    # Cálculo del interés compuesto
    return principal * (pow((1 + rate / 100), time))


def plot_barras(df, apilado=True, rotulos=['','','']):
    """
    Función para dibujar gráfico de barras.
    Entradas:
            df:        Los datos se pasan en formato DataFrame
            stacked:   Se permite dibujar las barras contiguas o apiladas
            rotulos:   Se etiquetan los ejes y el título. 
    """
    ax                = df.plot(kind='bar', stacked=apilado, color=['green','red','blue','yellow'], rot=0)
    ax.legend(loc='upper left')
    ax.set_xlabel(rotulos[0])
    ax.set_ylabel(rotulos[1])
    ax.set_title(rotulos[2])
    ax.grid()
    plt.show()

  
def ejercicio_anual_1(datos, interes):
    """
    Función para calcular el interés compuesto de un único ejercicio fiscal (anual). 
    
    Entradas:
            datos:   Dataframe con los datos de un ejercicio fiscal. Debe haber una fila por mes. 
            interés: Interés según unidad de tiempo base (diario, mensual, etc.)
    
    Devuelve: 
                    El mismo DataFrame con dos columnas extras. Una con el interes compuesto y otra con los resultados.
    Raises:
            ValueError: Si los valores de principal o time son negativos.
            TypeError:  Si las entradas no son numéricas.

    Ultima actualización:        12/2/2025          
    Por:                 cemc (c)
    """

    datos = datos.copy()   # Copia para evitar modificaciones no intencionadas    
    datos['time'] = 13 - datos.index.month

    # Validar valor del interes antes de llamar a compound_interest
    if interes is None:
        raise ValueError(f"El interés para el ejercicio {datos.index.year[0]} no está definido.")

    # Aplicar la función fila por fila
    datos['compuesto'] = datos.apply(lambda row: compound_interest(row['Depósito'], interes, row['time']), axis=1).round(2)
    
    # Agregar resultados
    datos['resultado'] = datos['compuesto'] - datos['Depósito']
    return datos

import pandas as pd

def ejercicio_anual(datos, interes):
    """
    Función para calcular el interés compuesto de un único ejercicio fiscal (anual). 
    
    Entradas:
            datos:   DataFrame con los datos de un ejercicio fiscal. Debe haber una fila por mes. 
            interes: Interés según unidad de tiempo base (diario, mensual, etc.)
    
    Devuelve: 
            DataFrame con dos columnas adicionales: 'compuesto' (interés compuesto) y 'resultado'.
    
    Raises:
            TypeError: Si 'datos' no es un DataFrame, su índice no es DatetimeIndex o 'Depósito' no es numérico.
            ValueError: Si 'interes' es negativo o si 'Depósito' contiene valores negativos.
    
    Última actualización: 12/2/2025          
    Por: cemc (c)
    """

    # Verificar que datos sea un DataFrame
    if not isinstance(datos, pd.DataFrame):
        raise TypeError("El argumento 'datos' debe ser un DataFrame de pandas.")

    # Verificar que el índice sea de tipo DatetimeIndex
    if not isinstance(datos.index, pd.DatetimeIndex):
        raise TypeError("El índice de 'datos' debe ser de tipo DatetimeIndex.")

    # Verificar que la columna 'Depósito' existe
    if 'Depósito' not in datos.columns:
        raise ValueError("El DataFrame no contiene la columna 'Depósito'.")

    # Verificar que 'Depósito' sea numérico
    if not pd.api.types.is_numeric_dtype(datos['Depósito']):
        raise TypeError("La columna 'Depósito' debe contener valores numéricos.")

    # Validar el valor de interes
    if not isinstance(interes, (int, float)):
        raise TypeError("El argumento 'interes' debe ser un número.")

    if interes < 0:
        raise ValueError("El argumento 'interes' no puede ser negativo.")

    # Crear una copia para evitar modificar el DataFrame original
    datos = datos.copy()

    # Calcular el tiempo restante en meses para cada fila
    datos['time'] = 13 - datos.index.month

    # Validar que el interés está definido para el año en cuestión
    if interes is None:
        raise ValueError(f"El interés para el ejercicio {datos.index.year[0]} no está definido.")

    # Aplicar la función de interés compuesto
    datos['compuesto'] = datos.apply(lambda row: compound_interest(row['Depósito'], interes, row['time']), axis=1).round(2)
    
    # Agregar resultados
    datos['resultado'] = datos['compuesto'] - datos['Depósito']
    return datos


def filtrar_enero(grupo):
    """
    Función para mantener solo la última operación de enero. 
    
    Entradas:
            grupo:  Es el resultado de agrupar un Dataframe por columna fecha. 
    
    Devuelve: 
                    El mismo grupo pero con el mes de enero modificado, dejando solo la ultima operacion del mes.
    Raises:
            ValueError: Si los valores de principal o time son negativos.
            TypeError:  Si las entradas no son numéricas.

    Ultima actualización:        12/2/2025          
    Por:                 cemc (c)
    """

# Verificar que 'grupo' sea un DataFrame
    if not isinstance(grupo, pd.DataFrame):
        raise TypeError("El argumento 'grupo' debe ser un DataFrame de pandas.")

    # Verificar que la columna 'Fecha' existe
    if 'Fecha' not in grupo.columns:
        raise ValueError("El DataFrame no contiene la columna 'Fecha'.")

    # Verificar que 'Fecha' sea de tipo datetime
    if not pd.api.types.is_datetime64_any_dtype(grupo['Fecha']):
        raise TypeError("La columna 'Fecha' debe ser de tipo datetime.")
        
    enero = grupo[grupo['Fecha'].dt.month == 1].copy()  # Copia para evitar modificaciones no intencionadas    
    if len(enero) > 1:
        return pd.concat([grupo[grupo['Fecha'].dt.month != 1], enero.iloc[[-1]]]).sort_values(['Fecha'])
    return grupo
    

