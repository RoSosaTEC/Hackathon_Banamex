import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
import joblib

print("⏳ Iniciando el pipeline de emergencia (TF-IDF + LightGBM)...")

# ==========================================
# 1. CARGA DE DATOS Y TARGETS
# ==========================================
# Cargamos el CSV que tiene el texto libre, el NPS y la columna de la categoría
df = pd.read_csv("../Data/datos-entrenamiento.csv", encoding="utf-8")

# Aseguramos que no haya nulos en el texto de queja
df['Verbalizacion'] = df['Verbalizacion'].fillna('').astype(str)

# Preparamos la variable objetivo (y) - Tus 50 categorías en texto
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(df['cluster_name'])

# ==========================================
# 2. VECTORIZACIÓN RÁPIDA (El sustituto de los embeddings)
# ==========================================
print("📦 Convirtiendo texto a números con TF-IDF...")
# Limitamos a las 5,000 palabras más importantes para que sea ultra rápido
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2)) 
X_tfidf = tfidf.fit_transform(df['Verbalizacion'])

# Convertimos la matriz dispersa de TF-IDF a un formato que LightGBM procesa volando
X_tfidf = X_tfidf.tocsr()

# ==========================================
# 3. AGREGAR EL NPS_RATE A LA MATRIZ
# ==========================================
# Como el NPS es un número tabular, lo añadimos como una columna extra al TF-IDF
from scipy.sparse import hstack
columna_nps = df['NPS_Rate'].values.reshape(-1, 1)
X_final = hstack([X_tfidf, columna_nps]).tocsr()

# ==========================================
# 4. DIVISIÓN PARA ENTRENAMIENTO Y EARLY STOPPING
# ==========================================
X_train, X_val, y_train, y_val = train_test_split(
    X_final, y_encoded, 
    test_size=0.2, 
    random_state=42, 
    stratify=y_encoded
)

# Convertir a los contenedores optimizados de LightGBM
train_data = lgb.Dataset(X_train, label=y_train)
val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)

# ==========================================
# 5. CONFIGURACIÓN DE PARÁMETROS Y GPU
# ==========================================
parametros = {
    'objective': 'multiclass',
    'num_class': len(label_encoder.classes_),
    'metric': 'multi_logloss',
    'learning_rate': 0.1,
    'class_weight': 'balanced', # Maneja el desbalance de las 50 clases
    'random_state': 42,
    'n_jobs': -1,
    'device_type': 'cpu' # <--- Activa la GPU. Si marca error por drivers, cambia a 'cpu'
}

# Callbacks para la barra de progreso simulada y Early Stopping
callbacks = [
    lgb.early_stopping(stopping_rounds=15, verbose=True), # Detiene si no mejora en 15 iteraciones
    lgb.log_evaluation(period=1) # Imprime el progreso en cada "epoch" / árbol
]

# ==========================================
# 6. ENTRENAMIENTO
# ==========================================
print("🚀 Entrenando LightGBM con aceleración...")
modelo_final = lgb.train(
    parametros,
    train_data,
    num_boost_round=200, # Máximo de iteraciones
    valid_sets=[val_data],
    callbacks=callbacks
)

# ==========================================
# 7. SERIALIZACIÓN INTELIGENTE (Para el Frontend)
# ==========================================
print("\n💾 Serializando artefactos para la API...")
# LightGBM guarda automáticamente la mejor iteración gracias al Early Stopping
joblib.dump(modelo_final, '../Models/modelo_emergencia_lgbm.pkl')
joblib.dump(label_encoder, '../Models/traductor_categorias.pkl')
joblib.dump(tfidf, '../Models/vectorizador_tfidf.pkl') # ¡VITAL! Hay que guardar el transformador de texto

print("✨ Pipeline concluido con éxito. ¡Estás listo para conectar el Front!")