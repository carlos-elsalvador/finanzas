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

app = Flask(__name__)

# Función para generar el gráfico comparativo por año
# Función para generar el gráfico comparativo por año o un gráfico de pastel
def generar_grafico2imagen(df, tipo):

    # fig, ax = plt.subplots()
    fig, ax = plt.subplots(figsize=(14, 4))  # Ajusta el ancho y alto

    if tipo == "barras":
        # 1/ Ingresos vs Gastos por categoria
        resultado = gastos_ingresos(df,categories)

        x = range(len(resultado["año"]))  # Posiciones en el eje X
        ancho = 0.3  # Ancho de las barras

        ax.bar(x, resultado["ingresos"], width=ancho, label="Ingresos", color="green", align="center")
        ax.bar([pos + ancho for pos in x], resultado["gastos"], width=ancho, label="Gastos", color="red", align="center")

        ax.set_xticks([pos + ancho / 2 for pos in x])
        ax.set_xticklabels(resultado["año"])
        ax.set_title("Comparación de Ingresos vs Gastos por Año")
        ax.set_xlabel("Año")
        ax.set_ylabel("Monto en USD")
        ax.legend()

    elif tipo == "pastel":
        # 2/ Gastos por categoria (pastel)   
        resultado  = df.groupby("categoria")["cargo"].sum().sort_values(ascending=False)

        ax.pie(resultado, labels=resultado.index, autopct="%1.1f%%", startangle=90, colors=plt.cm.Paired.colors)
        ax.set_title("Distribución de Gastos por Categoría")

    elif tipo == "calor":
        # 3/ Gastos por categoria (heat map).Por año y categoría, sumando los gastos.
        heatmap_data_anual = df.pivot_table(index="categoria", columns="año", values="cargo", aggfunc="sum", fill_value=0)
        # ax.figure()
        sns.heatmap(heatmap_data_anual, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)
        ax.set_title("Distribución de Gastos por Categoría")

    else:
        return None

    # Convertir la gráfica en imagen base64
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()

    return img_base64

# Ruta principal de la aplicación Flask
@app.route("/", methods=["GET", "POST"])
def index():
    img_base64 = None

# consulta MySQL
    consulta_sql = """
        SELECT fecha_tran, transaccion, abono, cargo, 
        YEAR(fecha_tran) AS año, MONTH(fecha_tran) AS mes, 
        SUBSTRING_INDEX(transaccion, ':', 1) AS etiquetaX
        FROM movimientos
        WHERE YEAR(fecha_tran) IS NOT NULL AND YEAR(fecha_tran) > 2015;
    """
# Se ejecuta la consulta a la BD
    df  = obtener_datos_df(host="localhost", user="carlos", psw="mc91067CEMC*", db="bac", consulta=consulta_sql)
    # Clasificar transacciones segun categoria
    df["categoria"] = df["transaccion"].apply(lambda transaction: classify_transaction(transaction, categories))
    # Eliminar la categoría "Otros gastos" debido a que son gastos aun no identificados o simplemente se han ignorado en categories
    df  = df[df["categoria"] != "Otros gastos"] 

    if request.method == "POST":
        opcion = request.form.get("opcion")
        img_base64 = generar_grafico2imagen(df, opcion)

    return render_template("index.html", img_base64=img_base64)

if __name__ == "__main__":
    app.run(debug=True)

