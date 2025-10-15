
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
