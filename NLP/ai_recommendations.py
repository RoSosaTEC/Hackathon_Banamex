# ai_recommendations.py

import os
import pandas as pd

from dotenv import load_dotenv
from groq import Groq

# ---------------------------------------------------
# LOAD ENV VARIABLES
# ---------------------------------------------------

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------------------------------------------------
# GENERATE AI RECOMMENDATIONS
# ---------------------------------------------------

def generar_recomendaciones(
    df_insights,
    segmento="Detractores",
    max_rows=30
):

    """
    Genera recomendaciones ejecutivas usando insights
    obtenidos mediante NLP y n-gramas.

    Parameters
    ----------
    df_insights : pd.DataFrame
        DataFrame con:
        - Segmento
        - Frase_Clave
        - Frecuencia

    segmento : str
        Segmento a analizar:
        - Detractores
        - Promotores
        - Pasivos

    max_rows : int
        Máximo número de insights enviados al modelo
    """

    # ---------------------------------------------------
    # VALIDACIONES
    # ---------------------------------------------------

    required_columns = [
        "Segmento",
        "Frase_Clave",
        "Frecuencia"
    ]

    for col in required_columns:

        if col not in df_insights.columns:

            return (
                f"Error: falta la columna '{col}' "
                "en df_insights."
            )

    # ---------------------------------------------------
    # FILTRAR SEGMENTO
    # ---------------------------------------------------

    df_segmento = df_insights[
        df_insights["Segmento"] == segmento
    ]

    if df_segmento.empty:

        return (
            f"No se encontraron insights "
            f"para el segmento '{segmento}'."
        )

    # ---------------------------------------------------
    # LIMITAR INSIGHTS
    # ---------------------------------------------------

    df_segmento = df_segmento.head(max_rows)

    # ---------------------------------------------------
    # CONSTRUIR TEXTO
    # ---------------------------------------------------

    insights_texto = ""

    for _, row in df_segmento.iterrows():

        insights_texto += (
            f"- Frase clave: {row['Frase_Clave']}\n"
            f"  Frecuencia: {row['Frecuencia']}\n\n"
        )

    # ---------------------------------------------------
    # PROMPT
    # ---------------------------------------------------

    prompt = f"""
    Eres un consultor senior especializado en:

    - Customer Experience (CX)
    - Transformación digital
    - Inteligencia de clientes
    - Instituciones financieras

    Analiza los siguientes insights obtenidos
    mediante NLP y análisis de comentarios NPS
    de clientes bancarios.

    El segmento analizado es:
    {segmento}

    Genera un reporte ejecutivo profesional con:

    # 1. Resumen Ejecutivo

    # 2. Principales Hallazgos
    - Explica patrones recurrentes
    - Detecta problemas o fortalezas frecuentes

    # 3. Riesgos Operativos
    - Riesgos para satisfacción
    - Riesgos reputacionales
    - Riesgos de retención de clientes

    # 4. Recomendaciones Accionables

    Para cada recomendación incluye:
    - Acción sugerida
    - Impacto esperado
    - Nivel de prioridad:
      - Alta
      - Media
      - Baja

    # 5. Conclusión Estratégica

    Mantén un tono:
    - Ejecutivo
    - Profesional
    - Claro
    - Orientado a negocio

    Insights detectados:

    {insights_texto}
    """

    # ---------------------------------------------------
    # GROQ REQUEST
    # ---------------------------------------------------

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",
                    "content": (
                        "Eres un experto senior en "
                        "customer experience para bancos."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.4
        )

        return response.choices[0].message.content

    # ---------------------------------------------------
    # ERROR HANDLING
    # ---------------------------------------------------

    except Exception as e:

        return (
            "Error generando recomendaciones:\n\n"
            f"{str(e)}"
        )


# ---------------------------------------------------
# OPTIONAL TEST
# ---------------------------------------------------

if __name__ == "__main__":

    # Ejemplo rápido de prueba

    data = {

        "Segmento": [
            "Detractores",
            "Detractores",
            "Detractores"
        ],

        "Frase_Clave": [
            "app lenta",
            "errores pago",
            "soporte tarda"
        ],

        "Frecuencia": [
            35,
            20,
            15
        ]
    }

    df_test = pd.DataFrame(data)

    resultado = generar_recomendaciones(
        df_test,
        segmento="Detractores"
    )

    print(resultado)