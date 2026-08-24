import os
import json
import requests
from datetime import datetime

# Endpoint v4.0 con parámetros de fecha obligatorios
BASE_URL = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/5"
OUTPUT_DIR = "data/bronze/bcra"

def ingest_bcra_data():
    """Consume la serie v4.0 del BCRA y guarda la respuesta en crudo."""
    try:
        # Parámetros de consulta
        today_str = datetime.now().strftime("%Y-%m-%d")
        params = {
            "desde": "2024-01-01",
            "hasta": today_str
        }

        response = requests.get(BASE_URL, params=params, verify=False, timeout=30)
        response.raise_for_status()
        raw_data = response.json()

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(OUTPUT_DIR, f"bcra_monetarias_5_{timestamp}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)

        print(f"[Bronze] Ingesta exitosa: {file_path}")
        return file_path

    except Exception as e:
        print(f"[Error] Falló la ingesta BCRA Bronze: {e}")
        raise

if __name__ == "__main__":
    ingest_bcra_data()
