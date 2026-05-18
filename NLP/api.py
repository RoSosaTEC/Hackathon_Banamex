from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analysis_service import run_analysis

# ---------------------------------------------------
# CREATE APP
# ---------------------------------------------------

app = FastAPI()

# ---------------------------------------------------
# ENABLE CORS
# ---------------------------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# ---------------------------------------------------
# ROOT ROUTE
# ---------------------------------------------------

@app.get("/")

def root():

    return {
        "message": "NLP API Running"
    }

# ---------------------------------------------------
# ANALYSIS ROUTE
# ---------------------------------------------------

@app.get("/analysis")

def analysis():

    results = run_analysis()

    return results