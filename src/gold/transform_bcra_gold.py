import os
import glob
import pandas as pd

SILVER_DIR = "data/silver/bcra"
GOLD_DIR = "data/gold/bcra"

def transform_to_gold():
    files = glob.glob(os.path.join(SILVER_DIR, "*.parquet"))
    if not files:
        raise FileNotFoundError("No se encontraron archivos en Silver.")
    
    silver_file = max(files, key=os.path.getctime)
    print(f"[Gold] Procesando: {silver_file}")
    df = pd.read_parquet(silver_file)

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    df_gold = df.groupby(["anio", "mes"]).agg(
        promedio_valor=("valor", "mean"),
        max_valor=("valor", "max"),
        min_valor=("valor", "min"),
        registros=("valor", "count")
    ).reset_index()

    df_gold["promedio_valor"] = df_gold["promedio_valor"].round(2)
    df_gold["updated_at"] = pd.Timestamp.now()

    os.makedirs(GOLD_DIR, exist_ok=True)
    output_path = os.path.join(GOLD_DIR, "kpi_monetarias_5_mensual.parquet")
    df_gold.to_parquet(output_path, index=False, engine="pyarrow")

    print(f"[Gold] Métricas generadas en: {output_path}")
    return output_path

if __name__ == "__main__":
    transform_to_gold()
