"""
Este archivo se encarga de juntar los 3 archivos txt
en uno solo csv, para facilitar el proceso de limpieza y análisis
de datos.
"""

import pandas as pd

# Lista de archivos a juntar
archivos = [
    "../Data/1_mitad_2025c.txt",
    "../Data/2_mitad_2025.txt",
    "../Data/1_mitad_2026.txt"
]

# Leer cada archivo y guardarlo en una lista de DataFrames
lista_dfs = []
for archivo in archivos:
    # Asegúrate de usar el mismo encoding y separador que funcionó para el primero
    _df = pd.read_csv(archivo, sep="\t", encoding="latin1") 
    lista_dfs.append(_df)

# Concatenar todos los DataFrames en uno solo
df_completo = pd.concat(lista_dfs, ignore_index=True)

# Guardar el DataFrame completo en un nuevo CSV
ruta_salida = "../Data/raw-data-all.csv"
df_completo.to_csv(ruta_salida, index=False)

print(f"Archivos combinados con éxito! Total de filas: {len(df_completo)}. Guardado en: {ruta_salida}")
