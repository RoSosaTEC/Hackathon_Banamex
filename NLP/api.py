from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import joblib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# INYECCIÓN DE MODELOS SERIALIZADOS (Tus archivos .pth y .pkl)
# --------------------------------------------------
try:
    tfidf = joblib.load('../Models/vectorizador_tfidf.pkl')
    traductor = joblib.load('../Models/traductor_categorias.pkl')
    # Cargar el modelo LightGBM en vez de PyTorch
    modelo_lgbm = joblib.load('../Models/modelo_emergencia_lgbm.pkl')
    
    print("✨ Modelos de IA cargados exitosamente (LightGBM).")
except Exception as e:
    print(f"🚨 Error al cargar los modelos de IA: {str(e)}")


# --------------------------------------------------
# CONTRATOS DE ENTRADA Y SALIDA PARA TU MODELO (Pydantic)
# --------------------------------------------------
class PeticionQueja(BaseModel):
    texto: str = Field(..., min_length=3)
    nps_rate: int = Field(..., ge=0, le=10)
    id_branch: str = Field(default="No especificada")

class RespuestaInferencia(BaseModel):
    texto_recibido: str
    nps_grupo: str
    categoria_abstraida: str
    alerta_gerencial: bool


# -------------------------
# LOAD DATA ON START (Código de tu compañero sin tocar)
# -------------------------
df = pd.read_csv(
    "../Data/datos-entrenamiento.csv",
    encoding="utf-8"
)

print("DATA LOADED:", df.shape)

df["Fecha respuesta"] = pd.to_datetime(df["Fecha respuesta"], errors="coerce")


# -------------------------
# ROOT
# -------------------------
@app.get("/")
def root():
    return {"message": "NLP API Running"}


# --------------------------------------------------
# NUEVO ENDPOINT: CLASIFICACIÓN EN TIEMPO REAL CON LIGHTGBM
# --------------------------------------------------
@app.post("/predict-feedback", response_model=RespuestaInferencia)
async def predict_feedback(datos: PeticionQueja):
    try:
        # Enrutador lógico de negocio para mapear el grupo NPS
        if datos.nps_rate <= 6:
            grupo_nps = "Detractor"
            alerta = True
        elif datos.nps_rate >= 9:
            grupo_nps = "Promotor"
            alerta = False
        else:
            grupo_nps = "Pasivo"
            alerta = False

        # Transformación del texto plano usando el TF-IDF serializado
        # Usamos sparse matrices para no gastar memoria innecesaria
        from scipy.sparse import hstack
        texto_features = tfidf.transform([datos.texto])
        
        # Concatenación del NPS Rate al final de las 5000 variables del texto
        columna_nps = np.array([float(datos.nps_rate)]).reshape(1, 1)
        vector_completo = hstack([texto_features, columna_nps]).tocsr()
        
        # Inferencia matemática express de LightGBM
        outputs = modelo_lgbm.predict(vector_completo)
        id_final = np.argmax(outputs[0])

        # Traducción del ID de vuelta a la categoría de texto de tus 50 targets
        categoria_servicio = str(traductor.inverse_transform([id_final])[0])

        return RespuestaInferencia(
            texto_recibido=datos.texto.strip(),
            nps_grupo=grupo_nps,
            categoria_abstraida=categoria_servicio,
            alerta_gerencial=alerta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el motor predictivo de LightGBM: {str(e)}")


# -------------------------
# FILTER ENDPOINT (Código de tu compañero sin tocar)
# -------------------------
@app.get("/filter-feedback")
def filter_feedback(
    id_branch: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None)
):

    temp = df.copy()

    # -------------------------
    # APPLY FILTERS ONLY IF EXIST
    # -------------------------

    if id_branch:
        temp = temp[temp["Id_branch"] == id_branch.strip()]

    if start_date:
        start_date = pd.to_datetime(start_date)
        temp = temp[temp["Fecha respuesta"] >= start_date]

    if end_date:
        end_date = pd.to_datetime(end_date)
        temp = temp[temp["Fecha respuesta"] <= end_date]

    return {
        "count": len(temp),
        "filters_used": {
            "id_branch": id_branch,
            "start_date": start_date,
            "end_date": end_date
        },
        "data": temp.to_dict(orient="records")
    }
