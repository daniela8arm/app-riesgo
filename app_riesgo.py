from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF
import re
import matplotlib
matplotlib.use('Agg')  # Evita errores en servidores sin entorno gráfico
import matplotlib.pyplot as plt
import nltk
from wordcloud import WordCloud
from nltk.corpus import stopwords

# ------------------------------------------------------------
# CONFIGURACIÓN INICIAL
# ------------------------------------------------------------

app = Flask(__name__)

# Rutas absolutas para que Render/Docker encuentren las carpetas
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
STATIC_FOLDER = os.path.join(os.getcwd(), "static")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# NOTA: NLTK se descarga en Dockerfile (NO usar nltk.download aquí)


# ------------------------------------------------------------
# FUNCIONES DE ANÁLISIS
# ------------------------------------------------------------

def extraer_texto_pdf(ruta_pdf):
    """Extrae el texto de un archivo PDF completo."""
    doc = fitz.open(ruta_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    doc.close()
    return texto


def buscar_patrones(texto):
    """Busca patrones financieros sospechosos en el texto."""
    patrones = [
        "material uncertainty",
        "going concern",
        "impairment",
        "waiver",
        "liquidity risk",
        "non-compliance",
        "estimates",
        "internal investigation",
        "losses",
        "reclassification",
        "change in accounting policies",
        "doubt on ability to continue",
        "conflict of interest",
        "misstatement",
        "irregularities",
        "overstatement",
        "embezzlement",
        "collusion",
        "off-balance sheet",
        "forensic accounting",
        "kickback",
        "whistleblower",
        "revenue recognition"
    ]

    resultados = {}

    for patron in patrones:
        ocurrencias = re.findall(patron, texto, re.IGNORECASE)

        filtro_contextual = re.findall(
            rf"(no\s+material\s+{patron}|without\s+significant\s+{patron}|no\s+instances\s+of\s+{patron})",
            texto,
            re.IGNORECASE
        )

        conteo_filtrado = len(ocurrencias) - len(filtro_contextual)
        if conteo_filtrado > 0:
            resultados[patron] = conteo_filtrado

    return resultados


def generar_wordcloud(texto, output_path):
    """Genera una nube de palabras."""
    stop_words = set(stopwords.words('english'))

    wc = WordCloud(
        stopwords=stop_words,
        background_color="white",
        width=800,
        height=400
    ).generate(texto)

    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=150)
    plt.close()


def evaluar_nivel_riesgo(resultados, texto):
    """Evalúa métricas de riesgo lingüístico."""
    total = sum(resultados.values())
    longitud = len(texto) if len(texto) > 0 else 1
    riesgo_relativo = (total / longitud) * 100

    if total <= 30 or riesgo_relativo < 0.02:
        nivel = "🟢 Riesgo bajo: lenguaje técnico normal, sin señales relevantes de alerta."
        color = "low"
    elif 31 <= total <= 60 or 0.02 <= riesgo_relativo < 0.05:
        nivel = "🟡 Riesgo moderado: se detectan algunos términos contables críticos, revisar contexto."
        color = "moderate"
    elif 61 <= total <= 100 or 0.05 <= riesgo_relativo < 0.1:
        nivel = "🟠 Riesgo alto: lenguaje asociado a deterioro o problemas financieros."
        color = "high"
    else:
        nivel = "🔴 Riesgo crítico: múltiples señales de alerta financiera. Requiere auditoría."
        color = "critical"

    return {
        "total_terminos": total,
        "longitud_texto": longitud,
        "riesgo_relativo": riesgo_relativo,
        "descripcion_nivel": nivel,
        "categoria_color": color
    }


# ------------------------------------------------------------
# RUTAS FLASK
# ------------------------------------------------------------

@app.route("/")
def inicio():
    return render_template("inicio_texto.html")


@app.route("/analizar", methods=["GET", "POST"])
def analizar():
    if request.method == "POST":
        archivo = request.files.get("pdf")

        if not archivo or archivo.filename == "":
            return render_template("analisis_texto.html", error="Por favor selecciona un archivo PDF.")

        if not archivo.filename.lower().endswith(".pdf"):
            return render_template("analisis_texto.html", error="Solo se permiten archivos en formato PDF.")

        filename = secure_filename(archivo.filename)
        ruta_pdf = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        archivo.save(ruta_pdf)

        texto = extraer_texto_pdf(ruta_pdf)
        resultados = buscar_patrones(texto)
        metrics = evaluar_nivel_riesgo(resultados, texto)

        wordcloud_path = os.path.join(STATIC_FOLDER, "wordcloud_riesgo.png")
        generar_wordcloud(texto, wordcloud_path)

        patrones_ordenados = sorted(resultados.items(), key=lambda x: x[1], reverse=True)

        return render_template(
            "resultado_texto.html",
            nombre_archivo=filename,
            patrones=patrones_ordenados,
            metrics=metrics,
            image_path="/static/wordcloud_riesgo.png"
        )

    return render_template("analisis_texto.html")


if __name__ == "__main__":
    app.run(debug=True)
