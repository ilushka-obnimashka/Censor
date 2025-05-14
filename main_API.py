import traceback
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from ultralytics.utils.checks import cuda_is_available

from main_file_processor import process_file
from utils import TempFilesManager
from utils import minio_client

app = FastAPI()


class ProcessRequest(BaseModel):
    key: str
    black_list: List[str]
    pixelation: bool = True


@app.post("/process/")
async def process_media(request: ProcessRequest):
    try:
        print (cuda_is_available())
        bucket = "uploads"
        local_input_path = minio_client.download_file(bucket, request.key, "temp_files")

        # Обработка файла
        processed_path = process_file(local_input_path, request.black_list, request.pixelation)

        # Загрузка обратно в MinIO
        result_key = minio_client.upload_file(bucket, processed_path)

        # Очистка временных файлов
        TempFilesManager().cleanup()

        return {"result_key": result_key}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main_API:app", host="0.0.0.0", port=8000, reload=True)