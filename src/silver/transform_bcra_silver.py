import os
import json
import glob
import pandas as pd

BRONZE_DIR = "data/bronze/bcra"
SILVER_DIR = "data/silver/bcra"

def get_latest_bronze_file():
    files = glob.glob(os.path.join(BRONZE_DIR, "*.json"))
    if not files:
        raise FileNotFoundError("No se encontraron archivos en Bronze.")
    return max(files, key=os.path.getctime)

def transform_to_silver():
    latest_file = get_latest_bronze_file()
    print(f"[Silver] Procesando: {latest_file}")
    
    with open(latest_file, "r", encoding="utf-8") as f:
        raw_json = json.load(f)

    if isinstance(raw_json, dict) and "results" in raw_json:
        data = raw_json["results"]
    elif isinstance(raw_json, list):
        data = raw_json
    else:
        data = [raw_json]

    df = pd.DataFrame(data)
    df.columns = df.columns.str.lower()

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df = df.dropna(subset=["fecha", "valor"]).drop_duplicates()
    df["processed_at"] = pd.Timestamp.now()

    os.makedirs(SILVER_DIR, exist_ok=True)
    output_path = os.path.join(SILVER_DIR, "bcra_monetarias_5_clean.parquet")
    df.to_parquet(output_path, index=False, engine="pyarrow")
    
    print(f"[Silver] Archivo guardado: {output_path}")
    return output_path

if __name__ == "__main__":
    transform_to_silver()
