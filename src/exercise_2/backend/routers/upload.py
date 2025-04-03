from fastapi import APIRouter, UploadFile, HTTPException, File
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

from starlette.responses import JSONResponse

from src.exercise_2.backend.services.deduplicator import AdDeduplicator
from src.exercise_2.backend.services.xml_parser import parse_xml

router = APIRouter()
deduplicator = AdDeduplicator()

# Получаем абсолютный путь к шаблону
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Поднимаемся до exercise_2
TEMPLATE_PATH = BASE_DIR / "frontend" / "templates" / "index.html"


@router.post("/upload")
async def upload_xml(file: UploadFile = File(...)):
    try:
        # Проверка расширения файла
        if not file.filename.lower().endswith('.xml'):
            raise ValueError("Only XML files are allowed")

        # Логирование информации о файле
        print(f"\nReceived file: {file.filename}")
        print(f"Content type: {file.content_type}")

        # Обработка XML
        stats = await parse_xml(file, deduplicator)

        # Преобразуем объекты Ad в словари
        serializable_stats = {
            "total": stats["total"],
            "duplicates": stats["duplicates"],
            "new": stats["new"],
            "ads": [ad.dict() if hasattr(ad, 'dict') else ad for ad in stats["ads"]]
        }

        return JSONResponse({
            "status": "success",
            "message": f"Processed: {stats['new']} new, {stats['duplicates']} duplicates",
            "filename": file.filename,
            "stats": serializable_stats  # Используем сериализуемую версию
        })

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/", response_class=HTMLResponse)
async def main():
    if not TEMPLATE_PATH.exists():
        error_msg = f"HTML template not found at: {TEMPLATE_PATH}"
        print(error_msg)  # Для отладки
        raise HTTPException(status_code=500, detail=error_msg)

    try:
        return TEMPLATE_PATH.read_text(encoding='utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading template: {str(e)}")