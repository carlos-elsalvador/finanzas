
from finanzas import *

# Definir categorías y palabras clave asociadas
categories = {
    "Supermercado/hogar": ["SELECTOS", "SUPER:", "HOGAR:", "CARNES", "CARNICERIA"],
    "Servicios básicos": ["PAGO SERVICIO:", "IMPUESTO:", "SKYPE"],
    "Salud y bienestar": ["MED:", "PODOLOGO", "VET:"],
    "Restaurantes/Entreten.": ["RST:","CINE:", "MUSEO:","TEATRO", "MEMBER: IEEE", "NEW YORK TIMES", "CHOCO LECHE", "BOWLING"],
    "Ropa y accesorios": ["ROPA-ZAP:", "PERFUMERIA:"],
    "Viajes/transporte": ["VUELO:", "HOTEL:", "AUTOBUS:", "TREN:", "VISA:","UBER", "TAXI"],    
    "Retiro de cajeros": ["RETIRO NAC.:","RETIRO INT.:"],
    "Transferencias": ["TRANSF.:","RETIRO DE AHORRO"],
    "Otros gastos": []  # Para transacciones que no encajen en las anteriores
}


# Función para clasificar transacciones
def classify_transaction(transaction):
    for category, keywords in categories.items():
        if any(keyword in transaction for keyword in keywords):
            return category
    return "Otros gastos"

# Crear una función para extraer etiquetas de las transacciones
def extract_label(transaction):
    if ':' in transaction:
        return transaction.split(':')[0] + ':'
    return 'OTHER'


# Filtrar y agrupar datos por categoría
def top_subcategories(df, category, top_n=5):
    filtered_df = df[df['Categoria'] == category]
    subcategory_totals = filtered_df.groupby('Etiqueta')['Cargo'].sum()
    top_subcategories = subcategory_totals.nlargest(top_n).index
    return filtered_df[filtered_df['Etiqueta'].isin(top_subcategories)]


#Fecha Transaccion,Fecha Aplicada,Hora,Transaccion,Referencia,Cargo,Abono,Saldo,Canal,Categoria

main_dir              = '/home/carlos/workbenchPython/finanzas/datos/'
df                    = pd.read_csv(main_dir+'bac.csv', parse_dates=['Fecha_Tran'], dayfirst=True, decimal=".", thousands=',')  
#Cargos
ca                    = df[['Fecha_Tran', 'Transaccion', 'Cargo', 'Saldo']]
ca                    = ca[ca["Cargo"].notna()]

# Asegurar que no haya valores nulos en la columna "Transaccion"
ca["Transaccion"]     = ca["Transaccion"].fillna("").str.upper()

# Aplicar clasificación
ca["Categoria"] = ca["Transaccion"].apply(classify_transaction)

# Añadir una columna con las etiquetas extraídas
ca['Etiqueta'] = ca['Transaccion'].apply(extract_label)


# Eliminar la categoría "Otros gastos" y "Transferencias"
ca = ca[ca["Categoria"] != "Otros gastos"] 
ca = ca[ca["Categoria"] != "Transferencias"] 
# Agrupar por categoría y sumar los gastos
gastos_por_categoria = ca.groupby("Categoria")["Cargo"].sum().sort_values(ascending=False)

#PLOT. Barras. Gráfico de barras
plt.figure(figsize=(12, 3))
sns.barplot(x=gastos_por_categoria.values, y=gastos_por_categoria.index, hue=gastos_por_categoria.index, palette="viridis")
plt.xlabel("Total Gastado ($)", fontsize=12)
plt.ylabel("Categoría", fontsize=12)
plt.xticks(fontsize=10)  # Ajusta tamaño de números del eje X
plt.yticks(fontsize=10)  # Ajusta tamaño de texto en eje Y
plt.title("Distribución de Gastos por Categoría")
plt.show()

#PLOT. PIE CHART
plt.figure(figsize=(10, 6))
gastos_por_categoria.plot(kind="pie", autopct="%1.1f%%", startangle=140, cmap="tab10")
plt.ylabel("")  # Oculta el label de y
plt.title("Distribución de Gastos por Categoría")
plt.show()

#PLOT. HEAT MAP
# Asegurar que la columna 'Fecha_Tran' sea de tipo fecha
#ca["Fecha_Tran"] = pd.to_datetime(ca["Fecha_Tran"])

# Extraer año y mes
ca["Año"] = ca["Fecha_Tran"].dt.year
ca["Mes"] = ca["Fecha_Tran"].dt.month

# Agrupar por mes y categoría, sumando los gastos
#heatmap_data = ca.pivot_table(index="Categoria", columns="Mes", values="Cargo", aggfunc="sum", fill_value=0)
# Agrupar por año y categoría, sumando los gastos
heatmap_data_anual = ca.pivot_table(index="Categoria", columns="Año", values="Cargo", aggfunc="sum", fill_value=0)

# Crear el heatmap
plt.figure(figsize=(12, 4))
sns.heatmap(heatmap_data_anual, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)
plt.xlabel("Año")
plt.ylabel("Categoría")
plt.title("Mapa de Calor de Gastos por Categoría y Año")
plt.xticks(rotation=45)
plt.show()


# Obtener todas las categorías únicas
categorias_unicas = ca["Categoria"].unique()


# Generar un heatmap por cada categoría, dibujando año vs mes
#for categoria in categorias_unicas:
#    datos_categoria = ca[ca["Categoria"] == categoria]

    # Crear tabla pivote (Año como filas, Mes como columnas)
#    heatmap_data = datos_categoria.pivot_table(index="Año", columns="Mes", values="Cargo", aggfunc="sum", fill_value=0)
    
    # Graficar
#    plt.figure(figsize=(12, 4))
#    sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)
    
#    plt.xlabel("Mes")
#    plt.ylabel("Año")
#    plt.title(f"Mapa de Calor de Gastos: {categoria}")
#    plt.xticks(ticks=range(1, 13), labels=["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"])
#    plt.yticks(rotation=0)
#    plt.show()


for categoria in categorias_unicas:
    datos_categoria = top_subcategories(ca, categoria)

    # Extraer año y mes
    datos_categoria["Año"] = datos_categoria["Fecha_Tran"].dt.year
    datos_categoria["Mes"] = datos_categoria["Fecha_Tran"].dt.month

    # Crear tabla pivote (Etiqueta como filas, Año como columnas)
    heatmap_data = datos_categoria.pivot_table(index="Etiqueta", columns="Año", values="Cargo", aggfunc="sum", fill_value=0)
    
    # Graficar
    plt.figure(figsize=(12, 4))
    sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)
    
    plt.xlabel("Año")
    plt.ylabel("Etiqueta")
    plt.title(f"Mapa de Calor de Gastos: {categoria}")
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.show()

exit()

# Generar un heatmap por cada categoría, dibujando año vs subcategorias
for categoria in categorias_unicas:

    datos_categoria = top_subcategories(ca, categoria)
#    datos_categoria = ca[ca["Categoria"] == categoria]
    print(datos_categoria)
    # Crear tabla pivote (Categoria como filas,  Año como columnas)
    heatmap_data = datos_categoria.pivot_table(index="Transaccion", columns="Año", values="Cargo", aggfunc="sum", fill_value=0)
    
    # Graficar
    plt.figure(figsize=(12, 4))
    sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)
    
    plt.xlabel("Año")
    plt.ylabel("Categoria")
    plt.title(f"Mapa de Calor de Gastos: {categoria}")
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.show()




#****
# Contar el número de transacciones por categoría
#transacciones_por_categoria = ca["Categoria"].value_counts()
# Mostrar el resultado
#print(transacciones_por_categoria)


# Filtrar transacciones de "Otros gastos" y eliminar filas donde "Cargo" esté vacío
#otros_gastos = ca[(ca["Categoria"] == "Otros gastos") & ca["Cargo"].notna()]

# Guardar en un archivo CSV
#otros_gastos.to_csv("otros_gastos.csv", index=False)
#print("Archivo 'otros_gastos.csv' guardado correctamente sin filas con 'Cargo' vacío.")

