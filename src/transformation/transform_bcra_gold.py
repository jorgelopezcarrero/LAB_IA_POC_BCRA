import os
import glob
import pandas as pd

# Rutas de entrada y salida
SILVER_DIR = "data/silver/bcra"
GOLD_DIR = "data/gold/bcra"

def get_latest_silver_file():
    """Obtiene el archivo Parquet procesado en Silver."""
    files = glob.glob(os.path.join(SILVER_DIR, "*.parquet"))
    if not files:
        raise FileNotFoundError("No se encontraron archivos en la capa Silver.")
    return max(files, key=os.path.getctime)

def transform_to_gold():
    """Genera vistas analíticas y agregaciones de negocio para la capa Gold."""
    # 1. Lectura desde Silver
    silver_file = get_latest_silver_file()
    print(f"[Gold] Leyendo datos desde: {silver_file}")
    df = pd.read_parquet(silver_file)

    if df.empty:
        print("[Gold] El DataFrame de Silver está vacío. Finalizando proceso.")
        return None

    # 2. Agregaciones / Métricas de Negocio
    # Asumiendo columnas estándar como 'fecha', 'id_variable' (o 'descripcion') y 'valor'
    if "fecha" in df.columns:
        df["anio"] = df["fecha"].dt.year
        df["mes"] = df["fecha"].dt.month

        # Ejemplo de Agregación: Promedio y valor máximo mensual por variable
        group_cols = ["anio", "mes"]
        if "id_variable" in df.columns:
            group_cols.append("id_variable")
        elif "descripcion" in df.columns:
            group_cols.append("descripcion")

        df_gold = df.groupby(group_cols).agg(
            promedio_valor=("valor", "mean"),
            max_valor=("valor", "max"),
            min_valor=("valor", "min"),
            registros=("valor", "count")
        ).reset_index()

        # Redondeo de métricas
        df_gold["promedio_valor"] = df_gold["promedio_valor"].round(2)
    else:
        # Si no hay fecha, se mantiene el dataset con las métricas consolidadas
        df_gold = df.copy()

    # Metadato de actualización
    df_gold["updated_at"] = pd.Timestamp.now()

    # 3. Persistencia en Capa Gold (Parquet y CSV para fácil consumo)
    os.makedirs(GOLD_DIR, exist_ok=True)
    
    parquet_path = os.path.join(GOLD_DIR, "kpi_bcra_mensual.parquet")
    csv_path = os.path.join(GOLD_DIR, "kpi_bcra_mensual.csv")

    df_gold.to_parquet(parquet_path, index=False, engine="pyarrow")
    df_gold.to_csv(csv_path, index=False, encoding="utf-8")

    print(f"[Gold] Capa Gold generada exitosamente:")
    print(f"       - Parquet: {parquet_path}")
    print(f"       - CSV:     {csv_path}")

    return parquet_path

if __name__ == "__main__":
    transform_to_gold()
