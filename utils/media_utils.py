from aiogram.types import FSInputFile


def resolve_photo_source(file_id: str, file_path: str):
    file_id = (file_id or "").strip()
    if file_id:
        return file_id
    return FSInputFile(file_path)
