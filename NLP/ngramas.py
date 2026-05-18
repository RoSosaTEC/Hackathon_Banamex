import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from ai_recommendations import generar_recomendaciones
from risk_analysis import analizar_riesgos# 1. Cargar tu dataset limpio
df_final = pd.read_csv("../Data/clean-data-all.csv", encoding="utf-8")

# Stop words bancarias para limpiar el ruido
stop_words_banco = [
    'que', 'de', 'la', 'en', 'el', 'un', 'una', 'los', 'las', 'por', 'con', 
    'para', 'es', 'muy', 'no', 'del', 'al', 'se', 'lo', 'me', 'mi', 'su', 
    'sus', 'ya', 'pero', 'como', 'más', 'mas', 'porque', 'cuando', 'este', 
    'esta', 'son', 'sin', 'todo', 'bien', 'mal', 'banco', 'servicio', 
    'atencion', 'cliente', 'fue', 'mis', 'todas'
]

def extraer_ngramas_df(corpus, segmento_nombre, top_k=30):
    """
    Extrae n-gramas (de 2 y 3 palabras) y los devuelve como un DataFrame.
    """
    # ngram_range=(2,3) extrae tanto bigramas como trigramas
    vec = CountVectorizer(ngram_range=(2, 3), stop_words=stop_words_banco).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0) 
    
    # Crear lista de tuplas (palabra, frecuencia)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    # Ordenar de mayor a menor frecuencia
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)[:top_k]
    
    # Convertir a DataFrame
    df_ngramas = pd.DataFrame(words_freq, columns=['Frase_Clave', 'Frecuencia'])
    df_ngramas['Segmento'] = segmento_nombre
    
    return df_ngramas

# 2. Separar los textos (Asumiendo que la columna se llama NPS_GROUP)
textos_detractores = df_final[df_final['NPS_GROUP'] == 'Detractor']['Verbalizacion'].dropna()
textos_promotores = df_final[df_final['NPS_GROUP'] == 'Promotor']['Verbalizacion'].dropna()
textos_pasivos = df_final[df_final['NPS_GROUP'] == 'Pasivo']['Verbalizacion'].dropna()

# 3. Generar los DataFrames de n-gramas (sacaremos el Top 50 de cada uno)
df_ngramas_detractores = extraer_ngramas_df(textos_detractores, 'Detractores', top_k=50)
df_ngramas_promotores = extraer_ngramas_df(textos_promotores, 'Promotores', top_k=50)
df_ngramas_pasivos = extraer_ngramas_df(textos_pasivos, 'Pasivos', top_k=50)

# 4. Unir ambos resultados en una sola tabla
df_insights = pd.concat([df_ngramas_detractores, df_ngramas_promotores, df_ngramas_pasivos], ignore_index=True)

# 5. Exportar para el equipo
#ruta_exportacion = "../Data/ngramas_para_recomendaciones.csv"
#df_insights.to_csv(ruta_exportacion, index=False, encoding="utf-8")

#print(f"¡Listo! Archivo exportado exitosamente en: {ruta_exportacion}")
print(df_insights.head(10)) # Mostrar una probadita de cómo quedó

reporte_detractores = generar_recomendaciones(
    df_insights,
    segmento="Detractores"
)

print("\n")
print("=" * 80)
print("REPORTE IA - DETRACTORES")
print("=" * 80)
print("\n")

print(reporte_detractores)

risk_results = analizar_riesgos(df_insights)

print(risk_results)