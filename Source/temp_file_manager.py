import os
import tempfile


def singelton(cls):
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances.keys():
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper


@singelton
class TempFilesManager:
    """Менеджер для работы с временными файлами и директориями.

    Реализует паттерн Singleton. Автоматически отслеживает и удаляет созданные
    временные файлы и директории при вызове cleanup().

    Атрибуты:
        temp_files (list): Список путей к временным файлам.
        temp_dirs (list): Список путей к временным директориям.
    """

    def __init__(self):
        self.temp_files = []
        self.temp_dirs = []

    def create_temp_file(self, suffix=None, prefix=None):
        """Создает именованный временный файл.

        Args:
            suffix (str, optional): Суффикс имени файла.
            prefix (str, optional): Префикс имени файла.

        Returns:
            NamedTemporaryFile: Объект временного файла.
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=prefix)
        self.temp_files.append(temp_file.name)
        return temp_file

    def create_temp_dir(self, suffix=None, prefix=None):
        """Создает временную директорию.

        Args:
            suffix (str, optional): Суффикс имени директории.
            prefix (str, optional): Префикс имени директории.

        Returns:
            TemporaryDirectory: Объект временной директории.
        """
        temp_dir = tempfile.TemporaryDirectory(suffix=suffix, prefix=prefix)
        self.temp_dirs.append(temp_dir.name)
        return temp_dir

    def cleanup(self):
        """Удаляет все зарегистрированные временные файлы и директории."""
        for file in self.temp_files:
            if os.path.exists(file):
                os.remove(file)
        for dir in self.temp_dirs:
            if os.path.exists(dir):
                os.rmdir(dir)
