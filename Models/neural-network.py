import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from tqdm import tqdm
import joblib

# ==========================================
# 1. ASIGNACIÓN DE DISPOSITIVO (GPU/CPU)
# ==========================================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🧠 Red Neuronal de Emergencia entrenando en: {device}")

# ==========================================
# 2. CARGA Y PREPARACIÓN DE DATOS
# ==========================================
df = pd.read_csv("../Data/datos-entrenamiento.csv", encoding="utf-8")
df['Verbalizacion'] = df['Verbalizacion'].fillna('').astype(str)

# Vectorización rápida con TF-IDF (Top 5,000 palabras/frases clave)
print("📦 Extrayendo características con TF-IDF...")
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_tfidf = tfidf.fit_transform(df['Verbalizacion']).tocsr()

# Extraer el NPS Rate como arreglo numérico
X_nps = df['NPS_Rate'].values.reshape(-1, 1)

# Codificar las 50 categorías de texto a números (0 a 49)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(df['cluster_name'])
num_clases = len(label_encoder.classes_)

# Separar en Entrenamiento (70%), Validación (15%) y Test (15%)
indices = np.arange(df.shape[0])
idx_train, idx_temp, y_train, y_temp = train_test_split(indices, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded)
idx_val, idx_test, y_val, y_test = train_test_split(idx_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

# Calcular pesos para combatir el desbalance de las 50 categorías
pesos_clase = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
criterion = nn.CrossEntropyLoss(weight=torch.FloatTensor(pesos_clase).to(device))

# ==========================================
# 3. DATASET PERSONALIZADO PARA MATRICES DISPERSAS
# ==========================================
# Esta clase toma pedazos dispersos de TF-IDF y los vuelve densos al vuelo para la GPU
class DatasetBancario(Dataset):
    def __init__(self, matriz_tfidf, arreglo_nps, etiquetas, indices_seleccionados):
        self.tfidf = matriz_tfidf[indices_seleccionados]
        self.nps = arreglo_nps[indices_seleccionados]
        self.etiquetas = etiquetas

    def __len__(self):
        return self.tfidf.shape[0]

    def __getitem__(self, idx):
        # Convertir la fila dispersa de TF-IDF a un vector denso normal de numpy
        fila_tfidf = self.tfidf[idx].toarray().astype(np.float32).squeeze()
        valor_nps = self.nps[idx].astype(np.float32)
        
        # Concatenar TF-IDF (5000) + NPS (1) = Vector de entrada de 5001 dimensiones
        vector_x = np.append(fila_tfidf, valor_nps)
        
        return torch.FloatTensor(vector_x), torch.tensor(self.etiquetas[idx], dtype=torch.long)

# Crear los cargadores de datos por bloques (Batches)
train_loader = DataLoader(DatasetBancario(X_tfidf, X_nps, y_train, idx_train), batch_size=256, shuffle=True)
val_loader = DataLoader(DatasetBancario(X_tfidf, X_nps, y_val, idx_val), batch_size=256, shuffle=False)

# ==========================================
# 4. ARQUITECTURA DE LA RED NEURONAL MULTICAPA
# ==========================================
class ClasificadorNPSTfIdf(nn.Module):
    def __init__(self, input_dim, num_clases):
        super(ClasificadorNPSTfIdf, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.4), # Dropout alto para evitar que memorice las palabras exactas (Overfitting)
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_clases)
        )
        
    def forward(self, x):
        return self.net(x)

# Dimensión de entrada: 5000 de TF-IDF + 1 de NPS = 5001
dimension_entrada = X_tfidf.shape[1] + 1
modelo_nn = ClasificadorNPSTfIdf(dimension_entrada, num_clases).to(device)
optimizer = optim.AdamW(modelo_nn.parameters(), lr=0.001, weight_decay=0.01)

# ==========================================
# 5. CONTROL DE EARLY STOPPING Y ENTRENAMIENTO
# ==========================================
max_epochs = 30
patience = 4
epochs_sin_mejora = 0
mejor_loss_val = float('inf')

print("🚀 Iniciando entrenamiento de la Red Neuronal...")

for epoch in range(max_epochs):
    modelo_nn.train()
    loss_entrenamiento = 0
    
    # Barra de progreso interactiva por cada Época
    loop_entrenamiento = tqdm(train_loader, desc=f"Epoch {epoch+1}/{max_epochs} [Train]")
    for batch_X, batch_y in loop_entrenamiento:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        
        outputs = modelo_nn(batch_X)
        loss = criterion(outputs, batch_y)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        loss_entrenamiento += loss.item()
        loop_entrenamiento.set_postfix(loss=loss.item())
        
    # Fase de Validación para revisar Overfitting (Parada Temprana)
    modelo_nn.eval()
    loss_val_total = 0
    with torch.no_grad():
        for batch_X, batch_y in val_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = modelo_nn(batch_X)
            loss_val_total += criterion(outputs, batch_y).item()
            
    loss_val_promedio = loss_val_total / len(val_loader)
    print(f" Loss Validación: {loss_val_promedio:.4f}")
    
    # GUARDADO INTELIGENTE (Checkpoint seguro)
    if loss_val_promedio < mejor_loss_val:
        mejor_loss_val = loss_val_promedio
        epochs_sin_mejora = 0
        # Sobrescribe el archivo únicamente si el modelo es el mejor hasta la fecha
        torch.save(modelo_nn.state_dict(), '../Models/mejor_red_neuronal_emergencia.pth')
        joblib.dump(label_encoder, '../Models/traductor_categorias.pkl')
        joblib.dump(tfidf, '../Models/vectorizador_tfidf.pkl')
        print(" 🔥 ¡Nuevo récord! Pesos y transformadores actualizados de forma segura.")
    else:
        epochs_sin_mejora += 1
        
    # Gatillo del Early Stopping
    if epochs_sin_mejora >= patience:
        print(f" Early Stopping activado. El modelo detuvo su entrenamiento en la época {epoch+1} para evitar sobreajuste.")
        break