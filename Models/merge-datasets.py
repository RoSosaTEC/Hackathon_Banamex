import pandas as pd
import os

dir_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_promotores = os.path.join(dir_base, "Data", "promotores_clusters.csv")
file_detractores = os.path.join(dir_base, "Data", "detractores_pasivos_clusters.csv")
file_out = os.path.join(dir_base, "Data", "datos-entrenamiento.csv")

print("Cargando archivos CSV...")
df_promotores = pd.read_csv(file_promotores, encoding='utf-8')
df_detractores = pd.read_csv(file_detractores, encoding='utf-8')

print("Concatenando DataFrames...")
df_final = pd.concat([df_promotores, df_detractores], ignore_index=True)

print("Guardando archivo final...")
df_final.to_csv(file_out, index=False, encoding='utf-8')

print(f"¡Listo! Archivo guardado como {file_out} con {len(df_final)} registros.")
