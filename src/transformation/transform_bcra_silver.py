import os
import glob
import pandas as pd

# Rutas de entrada y salida
BRONZE_DIR = "data/bronze/bcra"
SILVER_DIR = "data/silver/bcra"

def get_latest_bronze_file():
    """Obtiene el archivo JSON más reciente generado en la capa Bronze."""
    files = glob.glob(os.path.join(BRONZE_DIR, "*.json"))
    if not files:
        raise FileNotFoundError("No se encontraron archivos en la capa Bronze.")
    return max(files, key=os.path.getctime)

def transform_to_silver():
    """Limpia, estandariza y valida los datos de Bronze para Silver."""
    # 1. Lectura del último estado crudo
    latest_file = get_latest_bronze_file()
    print(f"[Silver] Leyendo datos desde: {latest_file}")
    df_raw = pd.read_json(latest_file)

    # 2. Transformaciones y Limpieza
    # Normalización / aplanado si la respuesta de la API venía anidada (ej. clave 'results')
    if "results" in df_raw.columns:
        df = pd.json_normalize(df_raw["results"])
    else:
        df = df_raw.copy()

    # Estandarizar nombres de columnas a snake_case
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(".", "_")
    )

    # Conversión de tipos de datos (ajustar según los campos reales del BCRA)
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    if "valor" in df.columns:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Tratamiento de duplicados y nulos esenciales
    df = df.drop_duplicates()
    df = df.dropna(subset=["fecha", "valor"]) if "fecha" in df.columns and "valor" in df.columns else df

    # Metadatos de auditoría
    df["processed_at"] = pd.Timestamp.now()

    # 3. Persistencia en Capa Silver (Formato Parquet)
    os.makedirs(SILVER_DIR, exist_ok=True)
    output_path = os.path.join(SILVER_DIR, "bcra_variables_clean.parquet")
    
    df.to_parquet(output_path, index=False, engine="pyarrow")
    print(f"[Silver] Transformación completada. Archivo guardado en: {output_path}")

    return output_path

if __name__ == "__main__":
    transform_to_silver()
