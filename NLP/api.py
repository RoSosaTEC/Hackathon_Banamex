from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# LOAD CSV
# ---------------------------------------------------

df = pd.read_csv(
    "../Data/datos-entrenamiento.csv",
    encoding="utf-8"
)

df["Fecha respuesta"] = pd.to_datetime(
    df["Fecha respuesta"],
    errors="coerce"
)

print("DATA LOADED:", df.shape)

# ---------------------------------------------------
# ROOT
# ---------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "NLP API Running"
    }

# ---------------------------------------------------
# FILTER ENDPOINT
# ---------------------------------------------------

@app.get("/filter-feedback")
def filter_feedback(
    id_branch: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None)
):

    temp = df.copy()

    # ---------------------------------------------------
    # APPLY FILTERS
    # ---------------------------------------------------

    if id_branch:

        temp = temp[
            temp["Id_branch"] == id_branch.strip()
        ]

    if start_date:

        start = pd.to_datetime(start_date)

        temp = temp[
            temp["Fecha respuesta"] >= start
        ]

    if end_date:

        end = pd.to_datetime(end_date)

        temp = temp[
            temp["Fecha respuesta"] <= end
        ]

    # ---------------------------------------------------
    # CLEAN JSON VALUES
    # ---------------------------------------------------

    # datetime -> string
    temp["Fecha respuesta"] = (
        temp["Fecha respuesta"]
        .astype(str)
    )

    # replace invalid float values
    temp = temp.replace(
        [np.inf, -np.inf],
        None
    )

    # replace NaN
    temp = temp.fillna("")

    # ---------------------------------------------------
    # LIMIT RESULTS (IMPORTANT)
    # ---------------------------------------------------

    temp = temp.head(5000)

    # ---------------------------------------------------
    # RETURN
    # ---------------------------------------------------

    return {
        "count": int(len(temp)),
        "filters_used": {
            "id_branch": id_branch,
            "start_date": start_date,
            "end_date": end_date
        },
        "data": temp.to_dict(orient="records")
    }