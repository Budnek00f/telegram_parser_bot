import os
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

async def download_file(file_obj, file_type: str, temp_dir: str) -> str:
    """Скачивает файл и возвращает путь к нему"""
    os.makedirs(temp_dir, exist_ok=True)
    
    file_extension = get_file_extension(file_obj, file_type)
    filename = f"{uuid4()}{file_extension}"
    file_path = os.path.join(temp_dir, filename)
    
    file = await file_obj.get_file()
    await file.download_to_drive(file_path)
    
    return file_path

def get_file_extension(file_obj, file_type: str) -> str:
    if file_type == "photo":
        return ".jpg"
    elif file_type == "document":
        file_name = getattr(file_obj, 'file_name', None)
        if file_name:
            return os.path.splitext(file_name)[1] or ".dat"
    return ".dat"

def cleanup_file(file_path: str):
    """Удаляет временный файл"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File cleaned up: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")