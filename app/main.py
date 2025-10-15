import os
import requests
import pandas as pd

EXCEL_FILE = "tracks blum.xlsx"
EXCEL_URL = "https://raw.githubusercontent.com/khrisriosblum/xbot-blum/main/tracks%20blum.xlsx"

if not os.path.exists(EXCEL_FILE):
    print(f"⚠️ '{EXCEL_FILE}' no encontrado. Descargando desde GitHub...")
    r = requests.get(EXCEL_URL)
    if r.status_code == 200:
        with open(EXCEL_FILE, "wb") as f:
            f.write(r.content)
        print(f"✅ Archivo '{EXCEL_FILE}' descargado correctamente.")
    else:
        print(f"❌ Error al descargar el archivo desde {EXCEL_URL}")

try:
    df = pd.read_excel(EXCEL_FILE)
    print(f"✅ Excel '{EXCEL_FILE}' cargado correctamente ({len(df)} filas).")
except Exception as e:
    print(f"❌ ERROR loading Excel: {e}")

from fastapi import FastAPI
from .scheduler import router as sched_router, start_scheduler

app = FastAPI(title="Khris X-bot-final", version="1.0.0")

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(sched_router, prefix="")
