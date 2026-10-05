from fastapi import FastAPI

from routes.auth import router as auth_router
from routes.health import router as health_router
from routes.predict import router as predict_router

app = FastAPI(
    title="Customer Support Intent API",
    description="API base para classificação de intenção de tickets de atendimento.",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(predict_router)
