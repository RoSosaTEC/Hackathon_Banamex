# risk_analysis.py

import pandas as pd

# ---------------------------------------------------
# CRITICAL KEYWORDS BY CATEGORY
# ---------------------------------------------------

CRITICAL_CATEGORIES = {

    "Pagos y Transferencias": [
        "error pago",
        "transferencia",
        "pago rechazado",
        "cobro",
        "duplicado",
        "saldo incorrecto"
    ],

    "Fraude y Seguridad": [
        "fraude",
        "robo",
        "hackeo",
        "clonaron",
        "bloqueo cuenta",
        "estafa"
    ],

    "App y Plataforma Digital": [
        "app lenta",
        "app falla",
        "error app",
        "no funciona",
        "caida sistema",
        "bug"
    ],

    "Atención al Cliente": [
        "soporte tarda",
        "mala atencion",
        "no responden",
        "fila larga",
        "espera"
    ],

    "Cajeros y Sucursales": [
        "cajero",
        "atm",
        "sucursal",
        "no habia efectivo",
        "deposito retenido"
    ]
}

# ---------------------------------------------------
# ANALYZE RISKS BY CATEGORY
# ---------------------------------------------------

def analizar_riesgos(df_insights):

    # ---------------------------------------------------
    # FILTER DETRACTORS
    # ---------------------------------------------------

    detractores = df_insights[
        df_insights["Segmento"] == "Detractores"
    ]

    # ---------------------------------------------------
    # INITIAL STRUCTURE
    # ---------------------------------------------------

    category_results = []

    total_global_score = 0

    # ---------------------------------------------------
    # PROCESS EACH CATEGORY
    # ---------------------------------------------------

    for category, keywords in CRITICAL_CATEGORIES.items():

        category_score = 0

        matched_issues = []

        total_frequency = 0

        # -----------------------------------------------
        # SEARCH MATCHES
        # -----------------------------------------------

        for _, row in detractores.iterrows():

            frase = str(row["Frase_Clave"]).lower()

            frecuencia = row["Frecuencia"]

            for keyword in keywords:

                if keyword in frase:

                    matched_issues.append({
                        "issue": row["Frase_Clave"],
                        "frequency": frecuencia
                    })

                    total_frequency += frecuencia

        # -----------------------------------------------
        # CALCULATE CATEGORY SCORE
        # -----------------------------------------------

        category_score += min(total_frequency / 3, 100)

        total_global_score += category_score

        # -----------------------------------------------
        # RISK LEVEL
        # -----------------------------------------------

        if category_score >= 80:

            risk_level = "CRÍTICO"

        elif category_score >= 60:

            risk_level = "ALTO"

        elif category_score >= 40:

            risk_level = "MEDIO"

        else:

            risk_level = "BAJO"

        # -----------------------------------------------
        # SAVE RESULT
        # -----------------------------------------------

        category_results.append({

            "category": category,

            "risk_score": round(category_score, 2),

            "risk_level": risk_level,

            "total_mentions": total_frequency,

            "main_issues": matched_issues[:5]
        })

    # ---------------------------------------------------
    # GLOBAL SCORE
    # ---------------------------------------------------

    global_score = min(
        round(total_global_score / len(CRITICAL_CATEGORIES), 2),
        100
    )

    # ---------------------------------------------------
    # GLOBAL RISK LEVEL
    # ---------------------------------------------------

    if global_score >= 80:

        global_risk = "CRÍTICO"

    elif global_score >= 60:

        global_risk = "ALTO"

    elif global_score >= 40:

        global_risk = "MEDIO"

    else:

        global_risk = "BAJO"

    # ---------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------

    return {

        "global_score": global_score,

        "global_risk": global_risk,

        "categories": sorted(
            category_results,
            key=lambda x: x["risk_score"],
            reverse=True
        )
    }


# ---------------------------------------------------
# OPTIONAL TEST
# ---------------------------------------------------

if __name__ == "__main__":

    data = {

        "Segmento": [
            "Detractores",
            "Detractores",
            "Detractores",
            "Detractores"
        ],

        "Frase_Clave": [
            "error pago app",
            "fraude tarjeta",
            "app lenta",
            "fila larga sucursal"
        ],

        "Frecuencia": [
            40,
            30,
            25,
            15
        ]
    }

    df_test = pd.DataFrame(data)

    result = analizar_riesgos(df_test)

    print(result)