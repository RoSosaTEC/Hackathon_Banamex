import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("🧪 Iniciando Test de Estrés y Validación de Modelos...")

# ==========================================
# 1. RECONSTRUIR EL SET DE TEST (EXAMEN OCULTO)
# ==========================================
df = pd.read_csv("../Data/datos-entrenamiento.csv", encoding="utf-8")
df['Verbalizacion'] = df['Verbalizacion'].fillna('').astype(str)

# Cargar el mismo transformador que guardaste en el entrenamiento
tfidf = joblib.load('../Models/vectorizador_tfidf.pkl')
traductor = joblib.load('../Models/traductor_categorias.pkl')

X_tfidf = tfidf.transform(df['Verbalizacion']).tocsr()
X_nps = df['NPS_Rate'].values.reshape(-1, 1)

from scipy.sparse import hstack
X_final = hstack([X_tfidf, X_nps]).tocsr()
y_encoded = traductor.transform(df['cluster_name'])

# Separamos exactamente con el mismo random_state para obtener el X_test puro
X_train, X_temp, y_train, y_temp = train_test_split(X_final, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded)
_, X_test, _, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

# ==========================================
# 2. EVALUAR LIGHTGBM
# ==========================================
# ==========================================
# 2. EVALUAR LIGHTGBM
# ==========================================
print("\n=== 🌲 EVALUANDO LIGHTGBM ===")
try:
    modelo_lgb = joblib.load('../Models/modelo_emergencia_lgbm.pkl')
    pred_lgb_raw = modelo_lgb.predict(X_test)
    
    if len(pred_lgb_raw.shape) > 1:
        pred_lgb = np.argmax(pred_lgb_raw, axis=1)
    else:
        pred_lgb = pred_lgb_raw
        
    acc_lgb = accuracy_score(y_test, pred_lgb) * 100
    print(f"🎯 Accuracy General LightGBM: {acc_lgb:.2f}%")
    print("\n Reporte por Categorías (Top 5 más comunes):")
    
    # LA SOLUCIÓN: Asegurar que todas las clases del traductor se lean como strings limpios
    nombres_clases = [str(clase) for clase in traductor.classes_]
    
    print(classification_report(y_test, pred_lgb, target_names=nombres_clases, digits=3, zero_division=0)[:800])
except Exception as e:
    print(f"No se pudo evaluar LightGBM: {e}")

# ==========================================
# 3. EVALUAR RED NEURONAL (PyTorch)
# ==========================================
print("\n=== 🧠 EVALUANDO RED NEURONAL (PYTORCH) ===")
try:
    class ClasificadorNPSTfIdf(nn.Module):
        def __init__(self, input_dim, num_clases):
            super(ClasificadorNPSTfIdf, self).__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.4),
                nn.Linear(256, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
                nn.Linear(128, num_clases)
            )
        def forward(self, x): return self.net(x)

    # Detectamos dinámicamente las clases del traductor
    nombres_clases = [str(clase) for clase in traductor.classes_]
    num_clases_real = len(nombres_clases)

    modelo_nn = ClasificadorNPSTfIdf(input_dim=5001, num_clases=num_clases_real)
    modelo_nn.load_state_dict(torch.load('../Models/mejor_red_neuronal_emergencia.pth', map_location=torch.device('cpu')))
    modelo_nn.eval()

    X_test_dense = torch.FloatTensor(X_test.toarray())
    
    with torch.no_grad():
        outputs = modelo_nn(X_test_dense)
        _, pred_nn = torch.max(outputs, 1)
        pred_nn = pred_nn.numpy()

    acc_nn = accuracy_score(y_test, pred_nn) * 100
    print(f"🎯 Accuracy General Red Neuronal: {acc_nn:.2f}%")
    print("\n Reporte por Categorías (Top 5 más comunes):")
    print(classification_report(y_test, pred_nn, target_names=nombres_clases, digits=3, zero_division=0)[:800])
except Exception as e:
    print(f"No se pudo evaluar la Red Neuronal: {e}")