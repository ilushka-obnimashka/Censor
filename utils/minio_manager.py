import os
import uuid
import re

from minio import Minio
from minio.error import S3Error

# Параметры подключения
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minio"
MINIO_SECRET_KEY = "minio123"
MINIO_SECURE = False  # True, если используешь https


class MinIOClient:
    def __init__(self, endpoint, access_key, secret_key, secure=False):
        # Создаем клиента для MinIO
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def upload_file(self, bucket_name, file_path):
        """
        Загружает файл в MinIO с сохранением исходного имени.
        :param bucket_name: имя бакета
        :param file_path: путь к локальному файлу
        """
        file_name = os.path.basename(file_path)
        file_id = str(uuid.uuid4())
        key = f"{file_id}_{file_name}"
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
            self.client.fput_object(bucket_name, key, file_path)
            print(f"Файл {key} успешно загружен в бакет {bucket_name}")
            return key
        except S3Error as err:
            print(f"Ошибка загрузки: {err}")
            return None

    def download_file(self, bucket_name, object_name, download_dir):
        """
        Скачивает файл из MinIO в указанную директорию, сохраняя имя объекта.
        :param bucket_name: имя бакета
        :param object_name: имя объекта в MinIO
        :param download_dir: путь к директории, куда сохранить файл
        :return: путь к скачанному файлу
        """
        try:
            # Убедимся, что директория существует
            os.makedirs(download_dir, exist_ok=True)

            base_name = os.path.basename(object_name)
            match = re.match(r"^[0-9a-fA-F\-]{36}_(.+)", base_name)
            clean_name = match.group(1) if match else base_name

            # Полный путь до файла (директория + имя файла из MinIO)
            download_path = os.path.join(download_dir, clean_name)

            self.client.fget_object(bucket_name, object_name, download_path)
            print(f"Файл {object_name} успешно скачан в {download_dir}")
            return download_path
        except S3Error as err:
            print(f"Ошибка скачивания: {err}")
            return None

    def delete_file(self, bucket_name, object_name):
        """
        Удаляет файл из MinIO.
        :param bucket_name: имя бакета
        :param object_name: имя объекта для удаления
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            print(f"Файл {object_name} успешно удален из бакета {bucket_name}")
        except S3Error as err:
            print(f"Ошибка удаления: {err}")

    def clear(self, bucket_name):
        """
        Удаляет все из MinIO.
        :param bucket_name: имя бакета
        """
        try:
            objects = self.client.list_objects(bucket_name)
            for obj in objects:
                self.client.remove_object(bucket_name, obj.object_name)
            print(f"Бакет {bucket_name} успешно зачищен")
        except S3Error as err:
            print(f"Ошибка удаления: {err}")

    def file_exists(self, bucket_name, object_name):
        """
        Проверяет, существует ли файл в бакете.
        :param bucket_name: имя бакета
        :param object_name: имя объекта
        :return: True, если файл существует, иначе False
        """
        try:
            objects = self.client.list_objects(bucket_name)
            for obj in objects:
                if obj.object_name == object_name:
                    return True
            return False
        except S3Error as err:
            print(f"Ошибка проверки существования файла: {err}")
            return False


# Создание единственного экземпляра клиента
minio_client = MinIOClient(
    endpoint=MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)