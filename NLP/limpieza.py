import pandas as pd
import re

# ==========================================
# 1. LECTURA DE DATOS
# ==========================================
# Leer con la codificación correcta (utf-8 resuelve el problema del Mojibake)
df = pd.read_csv("../Data/raw-data-all.csv", sep=",", encoding="utf-8")
df_clean = df.copy()

# ==========================================
# 2. PRE-PROCESAMIENTO BÁSICO
# ==========================================
# Quitar nulos y asegurar que la columna sea tipo string
df_clean = df_clean.dropna(subset=['Verbalizacion'])
df_clean['Verbalizacion'] = df_clean['Verbalizacion'].astype(str)

# ==========================================
# 3. NORMALIZACIÓN DE JERGA (Slang Expansion)
# ==========================================
# Diccionario con expresiones regulares y límites de palabra (\b)
diccionario_informal = {
    r'\bk\b': 'que', r'\bq\b': 'que', r'\bqe\b': 'que',
    r'\bxq\b': 'porque', r'\bxk\b': 'porque', r'\bporq\b': 'porque', r'\bpq\b': 'porque',
    r'\bpa\b': 'para', r'\bvdd\b': 'verdad',
    r'\bsrta\b': 'señorita', r'\bsrita\b': 'señorita',
    r'\bud\b': 'usted', r'\buds\b': 'ustedes',
    r'\bpls\b': 'por favor', r'\bporfa\b': 'por favor', r'\bxfa\b': 'por favor',
    r'\bbco\b': 'banco', r'\bcta\b': 'cuenta',
    r'\btdc\b': 'tarjeta de crédito', r'\btdd\b': 'tarjeta de débito',
    r'\bapp\b': 'aplicación', r'\bsuc\b': 'sucursal', r'\bsucs\b': 'sucursales',
    r'\bejec\b': 'ejecutivo', r'\bnum\b': 'número', r'\bcel\b': 'celular',
    r'\binfo\b': 'información', r'\bmsj\b': 'mensaje',
    r'\bmov\b': 'movimiento', r'\bmovs\b': 'movimientos', r'\bcompe\b': 'compensación',
    r'\bbn\b': 'bien', r'\btmb\b': 'también', r'\btmbn\b': 'también',
    r'\bmxo\b': 'mucho', r'\bmasomenos\b': 'mas o menos',
    r'\bexcel\b': 'excelente', r'\bpesimo\b': 'pésimo',
    r'\bhrs\b': 'horas', r'\bmin\b': 'minutos'
}

# Aplicamos el diccionario ignorando mayúsculas/minúsculas para capturar "XQ", "xq", "Xq"
# Se usa una función lambda con re.sub para aplicar el IGNORECASE de forma segura
for patron, reemplazo in diccionario_informal.items():
    regex_compilado = re.compile(patron, flags=re.IGNORECASE)
    df_clean['Verbalizacion'] = df_clean['Verbalizacion'].apply(lambda x: regex_compilado.sub(reemplazo, x))

# ==========================================
# 4. LIMPIEZA ESTRUCTURAL (Ruido y formato)
# ==========================================
# Limpiar espacios dobles, tabulaciones o saltos de línea extraños
df_clean['Verbalizacion'] = df_clean['Verbalizacion'].str.replace(r'\s+', ' ', regex=True).str.strip()

# Remover emojis raros o símbolos, PROTEGIENDO acentos y signos de puntuación clave (!?.,)
df_clean['Verbalizacion'] = df_clean['Verbalizacion'].str.replace(r'[^\w\s.,!?¡¿áéíóúÁÉÍÓÚñÑ]', '', regex=True)

# ==========================================
# 5. FILTRADO FINAL (Vacíos, duplicados y textos cortos)
# ==========================================
# Eliminar strings que quedaron vacíos tras la limpieza
df_clean = df_clean[df_clean['Verbalizacion'] != '']

# Eliminar duplicados absolutos de registro (asumiendo que RecordId es único por opinión)
df_clean = df_clean.drop_duplicates(subset=['RecordId'])

# Filtrar textos extremadamente cortos (Ruido que no aporta contexto)
df_clean['longitud_texto'] = df_clean['Verbalizacion'].str.len()
df_final = df_clean[df_clean['longitud_texto'] >= 5].drop(columns=['longitud_texto'])

# ==========================================
# 6. EXPORTACIÓN PARA EMBEDDINGS
# ==========================================
# Exportar asegurando la codificación y sin el índice de pandas
df_final.to_csv("../Data/clean-data-all.csv", index=False, encoding="utf-8")

print(f"¡Limpieza terminada! Registros finales listos para embeddings: {len(df_final)}")