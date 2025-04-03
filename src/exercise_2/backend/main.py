from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# Получаем абсолютный путь до статической директории
BASE_DIR = Path(__file__).resolve().parent.parent  # Поднимаемся до exercise_2
STATIC_DIR = BASE_DIR / "frontend" / "static"

# Проверяем существование директории
if not STATIC_DIR.exists():
    raise RuntimeError(f"Static files directory not found at: {STATIC_DIR}")

app = FastAPI()

# Подключаем роутер
from src.exercise_2.backend.routers.upload import router as upload_router
app.include_router(upload_router)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")