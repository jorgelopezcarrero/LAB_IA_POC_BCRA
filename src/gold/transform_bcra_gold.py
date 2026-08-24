import os
import glob
import pandas as pd

SILVER_DIR = "data/silver/bcra"
GOLD_DIR = "data/gold/bcra"

def get_latest_silver_file():
    files = glob.glob(os.path.join(SILVER_DIR, "*.parquet"))
    if not files:
        raise FileNotFoundError("No se encontraron archivos en la capa Silver.")
    return max(files, key=os.path.getctime)

def transform_to_gold():
    silver_file = get_latest_silver_file()
    print(f"[Gold] Leyendo datos desde Silver: {silver_file}")
    df = pd.read_parquet(silver_file)

    if df.empty:
        print("[Gold] No hay datos en Silver para procesar.")
        return None

    # Agregaciones finales de negocio
    if "fecha" in df.columns:
        df["anio"] = df["fecha"].dt.year
        df["mes"] = df["fecha"].dt.month

        group_cols = ["anio", "mes"]
        if "id_variable" in df.columns:
            group_cols.append("id_variable")

        df_gold = df.groupby(group_cols).agg(
            promedio_valor=("valor", "mean"),
            max_valor=("valor", "max"),
            min_valor=("valor", "min")
        ).reset_index()
    else:
        df_gold = df.copy()

    df_gold["updated_at"] = pd.Timestamp.now()

    os.makedirs(GOLD_DIR, exist_ok=True)
    output_path = os.path.join(GOLD_DIR, "kpi_bcra_mensual.parquet")
    df_gold.to_parquet(output_path, index=False, engine="pyarrow")
    
    print(f"[Gold] Capa Gold generada en: {output_path}")
    return output_path

if __name__ == "__main__":
    transform_to_gold()
