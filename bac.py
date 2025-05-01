from finanzas import *

# Definir categorías y palabras clave asociadas
categories = {
    "Supermercado/hogar": ["SELECTOS:", "SUPER:", "HOGAR:", "CARNICERIA:"],
    "Servicios básicos": ["SERVICIOS:", "IMPUESTO:", "TINTORERIA:"],
    "Salud y bienestar": ["MED:", "PODOLOGO:", "VET:"],
    "Restaurantes/Entreten.": ["RST:","CINE:", "MUSEO:", "MEMBER:", "RECREACION:", "LIBRERIA:"],
    "Ropa y accesorios": ["ROPA-ZAP:", "PERFUMERIA:"],
    "Viajes/transporte": ["VUELO:", "HOTEL:", "AUTOBUS:", "TREN:", "VISA:","UBER:"],    
    "Retiro de cajeros": ["RETIRO NAC.:","RETIRO INT.:"],
#    "Transferencias": ["TRANSF.:","DONACION:", "DEPOSITO DAP"],
    "Ingresos":["UES:", "CDA:","REEMBOLSO:", "REINTEGRO:"],
    "Otros gastos": []  # Para transacciones que no encajen en las anteriores
}


main_dir              = '/home/carlos/workbenchPython/finanzas/datos/'
df                    = pd.read_csv(main_dir+'bac.csv', parse_dates=['Fecha_Tran'], dayfirst=True, decimal=".", thousands=',')  
# df                    = pd.read_csv(main_dir+'bac.csv')

# PREPARACION DE DATOS
# Convertir con manejo de errores, errors="coerce" convierte valores inválidos en NaN, evitando fallos.
df['Fecha_Tran'] = pd.to_datetime(df['Fecha_Tran'], format='%Y-%m-%d', errors='coerce')

# Filtra datos anteriores a 2016 en base de datos original
mask                  = df['Fecha_Tran'] > datetime(2016,1,1)
df                    = df.loc[mask].copy()

# Asegurar que no haya valores nulos en la columna "Transaccion" y convertir a mayusculas
df["Transaccion"]     = df["Transaccion"].fillna("").str.upper()

# Aplicar clasificación
df["Categoria"]       = df["Transaccion"].apply(lambda transaction: classify_transaction(transaction, categories))

# Añadir una columna con las etiquetas extraídas
df['Etiqueta']        = df['Transaccion'].apply(extract_label)

# Extraer año y mes de la columna Fecha_Tran
df['Año']             = pd.to_datetime(df['Fecha_Tran']).dt.year
df['Mes']             = pd.to_datetime(df['Fecha_Tran']).dt.month

# Eliminar la categoría "Otros gastos" debido a que son gastos aun no identificados o simplemente se han ignorado en categories
df                    = df[df["Categoria"] != "Otros gastos"] 

# Se filtra para dejar unicamente un dataframe con los Cargos
ca                    = df[df["Cargo"].notna()]

# Agrupar por categoría y sumar los gastos anuales
gastos_por_categoria  = ca.groupby("Categoria")["Cargo"].sum().sort_values(ascending=False)
resumen_anual_ca      = ca.groupby('Año')[['Cargo']].sum()
resumen_anual_ab      = df.groupby('Año')[['Abono']].sum()
resumen_anual_ca['Ingresos'] = resumen_anual_ab['Abono']

# 1/ PLOT, BARRAS. GASTOS Vs INGRESOS. Agrupar por año para sumar gastos e ingresos
plot_barras(resumen_anual_ca, apilado=False, rotulos=['Year','US$','Ingresos vs Gastos'])

# 2/ PLOT, BARRAS. CATEGORIAS
plt.figure(figsize=(12, 3))
sns.barplot(x=gastos_por_categoria.values, y=gastos_por_categoria.index, hue=gastos_por_categoria.index, palette="viridis")
plt.grid()
plt.xlabel("Total Gastado ($)", fontsize=12)
plt.ylabel("Categoría", fontsize=12)
plt.xticks(fontsize=10)  # Ajusta tamaño de números del eje X
plt.yticks(fontsize=10)  # Ajusta tamaño de texto en eje Y
plt.title("Distribución de Gastos por Categoría")
plt.show()

# 3/ PLOT. PIE CHART
plt.figure(figsize=(10, 6))
gastos_por_categoria.plot(kind="pie", autopct="%1.1f%%", startangle=140, cmap="tab10")
plt.ylabel("")  # Oculta el label de y
plt.title("Distribución de Gastos por Categoría")
plt.show()

# 4/ PLOT, HEAT MAP. Por año y categoría, sumando los gastos.
heatmap_data_anual = ca.pivot_table(index="Categoria", columns="Año", values="Cargo", aggfunc="sum", fill_value=0)
plt.figure(figsize=(12, 4))
sns.heatmap(heatmap_data_anual, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)
plt.xlabel("Año")
plt.ylabel("Categoría")
plt.title("Gastos por Categoría y Año")
plt.xticks(rotation=45)
plt.show()

# PLOT.HEAT MAP. Generar un heatmap por cada categoría, dibujando año vs subcategorias
# Obtener todas las categorías únicas
categorias_unicas = ca["Categoria"].unique()

for categoria in categorias_unicas:
    datos_categoria = top_subcategories(ca, categoria)
    # Extraer año y mes
    datos_categoria["Año"] = datos_categoria["Fecha_Tran"].dt.year
    datos_categoria["Mes"] = datos_categoria["Fecha_Tran"].dt.month
    # Crear tabla pivote (Etiqueta como filas, Año como columnas)
    heatmap_data = datos_categoria.pivot_table(index="Etiqueta", columns="Año", values="Cargo", aggfunc="sum", fill_value=0)
    
    plt.figure(figsize=(12, 4))
    sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)
    plt.xlabel("Año")
    plt.ylabel("")
    plt.title(f"Gastos: {categoria}")
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.show()
#

# Generar un heatmap por cada categoría, dibujando año vs mes
for categoria in categorias_unicas:
    datos_categoria = ca[ca["Categoria"] == categoria]

    # Crear tabla pivote (Año como filas, Mes como columnas)
    heatmap_data = datos_categoria.pivot_table(index="Año", columns="Mes", values="Cargo", aggfunc="sum", fill_value=0)
    
    # Graficar
    plt.figure(figsize=(12, 4))
    sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)
    
    plt.xlabel("Mes")
    plt.ylabel("Año")
    plt.title(f"Gastos: {categoria}")
    plt.xticks(ticks=range(1, 13), labels=["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"])
    plt.yticks(rotation=0)
    plt.show()


