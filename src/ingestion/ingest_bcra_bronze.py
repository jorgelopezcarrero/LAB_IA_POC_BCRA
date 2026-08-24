import os
import json
import requests
from datetime import datetime

# Definición de rutas o endpoints
BCRA_API_URL = "https://api.bcra.gob.ar/principal/v1.0/variables" # Ejemplo
OUTPUT_DIR = "data/bronze/bcra"

def ingest_bcra_data():
    """Consume la API del BCRA y guarda la respuesta en crudo en la capa Bronze."""
    try:
        response = requests.get(BCRA_API_URL, verify=False)
        response.raise_for_status()
        raw_data = response.json()

        # Crear directorio si no existe
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Nombre del archivo con marca de tiempo (timestamp)
        today = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(OUTPUT_DIR, f"bcra_raw_{today}.json")

        # Guardar en capa Bronze
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)

        print(f"[Bronze] Ingesta exitosa: {file_path}")
        return file_path

    except Exception as e:
        print(f"[Error] Falló la ingesta BCRA Bronze: {e}")
        raise

if __name__ == "__main__":
    ingest_bcra_data()
