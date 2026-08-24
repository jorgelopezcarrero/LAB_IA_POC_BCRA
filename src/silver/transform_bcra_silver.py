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

    # Extraer la lista de resultados según la estructura devuelta
    if isinstance(raw_json, dict) and "results" in raw_json:
        data = raw_json["results"]
    elif isinstance(raw_json, dict) and "data" in raw_json:
        data = raw_json["data"]
    elif isinstance(raw_json, list):
        data = raw_json
    else:
        data = [raw_json]

    df = pd.DataFrame(data)
    
    # Imprimir columnas encontradas para inspección en el log de GitHub
    print(f"[Silver] Columnas encontradas en el JSON: {df.columns.tolist()}")

    # Estandarizar nombres de columnas a minúsculas
    df.columns = df.columns.str.lower()

    # Mapeo flexible de nombres comunes del BCRA
    rename_dict = {}
    for col in df.columns:
        if col in ["f", "fecha", "date"]:
            rename_dict[col] = "fecha"
        elif col in ["v", "valor", "value"]:
            rename_dict[col] = "valor"
    
    if rename_dict:
        df = df.rename(columns=rename_dict)

    # Transformación de datos si existen las columnas esperadas
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Limpieza condicional (solo aplica si las columnas existen)
    subset_cols = [c for c in ["fecha", "valor"] if c in df.columns]
    if subset_cols:
        df = df.dropna(subset=subset_cols)
    
    df = df.drop_duplicates()
    df["processed_at"] = pd.Timestamp.now()

    os.makedirs(SILVER_DIR, exist_ok=True)
    output_path = os.path.join(SILVER_DIR, "bcra_monetarias_5_clean.parquet")
    df.to_parquet(output_path, index=False, engine="pyarrow")
    
    print(f"[Silver] Archivo procesado correctamente en: {output_path}")
    return output_path

if __name__ == "__main__":
    transform_to_silver()
