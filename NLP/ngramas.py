import pandas as pd
import json

from sklearn.feature_extraction.text import CountVectorizer

from ai_recommendations import generar_recomendaciones
from risk_analysis import analizar_riesgos

# ---------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------

df_final = pd.read_csv(
    "../Data/clean-data-all.csv",
    encoding="utf-8"
)

# ---------------------------------------------------
# BANK STOP WORDS
# ---------------------------------------------------

stop_words_banco = [
    'que', 'de', 'la', 'en', 'el', 'un', 'una',
    'los', 'las', 'por', 'con', 'para', 'es',
    'muy', 'no', 'del', 'al', 'se', 'lo', 'me',
    'mi', 'su', 'sus', 'ya', 'pero', 'como',
    'más', 'mas', 'porque', 'cuando', 'este',
    'esta', 'son', 'sin', 'todo', 'bien',
    'mal', 'banco', 'servicio', 'atencion',
    'cliente', 'fue', 'mis', 'todas'
]

# ---------------------------------------------------
# NGRAM EXTRACTION
# ---------------------------------------------------

def extraer_ngramas_df(
    corpus,
    segmento_nombre,
    top_k=30
):
    """
    Extrae n-gramas (2 y 3 palabras)
    y devuelve un DataFrame.
    """

    vec = CountVectorizer(
        ngram_range=(2, 3),
        stop_words=stop_words_banco
    ).fit(corpus)

    bag_of_words = vec.transform(corpus)

    sum_words = bag_of_words.sum(axis=0)

    # IMPORTANT:
    # Convert numpy ints to Python ints
    # to avoid JSON serialization issues

    words_freq = [

        (
            word,
            int(sum_words[0, idx])
        )

        for word, idx in vec.vocabulary_.items()
    ]

    # Sort descending
    words_freq = sorted(
        words_freq,
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    # Create DataFrame
    df_ngramas = pd.DataFrame(
        words_freq,
        columns=[
            'Frase_Clave',
            'Frecuencia'
        ]
    )

    df_ngramas['Segmento'] = segmento_nombre

    return df_ngramas

# ---------------------------------------------------
# SPLIT TEXTS BY SEGMENT
# ---------------------------------------------------

textos_detractores = df_final[
    df_final['NPS_GROUP'] == 'Detractor'
]['Verbalizacion'].dropna()

textos_promotores = df_final[
    df_final['NPS_GROUP'] == 'Promotor'
]['Verbalizacion'].dropna()

textos_pasivos = df_final[
    df_final['NPS_GROUP'] == 'Pasivo'
]['Verbalizacion'].dropna()

# ---------------------------------------------------
# GENERATE NGRAMS
# ---------------------------------------------------

df_ngramas_detractores = extraer_ngramas_df(
    textos_detractores,
    'Detractores',
    top_k=50
)

df_ngramas_promotores = extraer_ngramas_df(
    textos_promotores,
    'Promotores',
    top_k=50
)

df_ngramas_pasivos = extraer_ngramas_df(
    textos_pasivos,
    'Pasivos',
    top_k=50
)

# ---------------------------------------------------
# COMBINE ALL INSIGHTS
# ---------------------------------------------------

df_insights = pd.concat(

    [
        df_ngramas_detractores,
        df_ngramas_promotores,
        df_ngramas_pasivos
    ],

    ignore_index=True
)

# ---------------------------------------------------
# GENERATE AI RECOMMENDATIONS
# ---------------------------------------------------

print("\nGenerando recomendaciones IA...\n")

reporte_detractores = generar_recomendaciones(
    df_insights,
    segmento="Detractores"
)

# ---------------------------------------------------
# RISK ANALYSIS
# ---------------------------------------------------

print("Calculando riesgos...\n")

risk_results = analizar_riesgos(
    df_insights
)

# ---------------------------------------------------
# DATAFRAME -> JSON
# ---------------------------------------------------

insights_json = df_insights.to_dict(
    orient="records"
)

# ---------------------------------------------------
# TOP NGRAMS BY SEGMENT
# ---------------------------------------------------

top_ngrams = {

    "Detractores": df_ngramas_detractores.to_dict(
        orient="records"
    ),

    "Promotores": df_ngramas_promotores.to_dict(
        orient="records"
    ),

    "Pasivos": df_ngramas_pasivos.to_dict(
        orient="records"
    )
}

# ---------------------------------------------------
# FINAL RESPONSE OBJECT
# ---------------------------------------------------

response = {

    "success": True,

    "summary": {

        "total_insights": len(df_insights),

        "segments": [
            "Detractores",
            "Promotores",
            "Pasivos"
        ]
    },

    "top_ngrams": top_ngrams,

    "insights": insights_json,

    "risk_analysis": risk_results,

    "ai_report": {

        "segment": "Detractores",

        # Force string conversion
        "content": str(reporte_detractores)
    }
}

# ---------------------------------------------------
# DEBUG PRINT
# ---------------------------------------------------

print("\nSTRUCTURE OF RESPONSE:\n")

print(response.keys())

print("\nJSON PREVIEW:\n")

print(
    json.dumps(
        response,
        ensure_ascii=False,
        indent=4
    )
)

# ---------------------------------------------------
# EXPORT JSON FILE
# ---------------------------------------------------

with open(
    "../Data/analysis_results.json",
    "w",
    encoding="utf-8"
) as json_file:

    json.dump(
        response,
        json_file,
        ensure_ascii=False,
        indent=4
    )

# ---------------------------------------------------
# SUCCESS MESSAGE
# ---------------------------------------------------

print("\nJSON exportado correctamente.")