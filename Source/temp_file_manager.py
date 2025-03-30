import os
import shutil


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
        self.temp_dir = self.create_temp_dir("temp_files")

    def create_temp_file(self, file_name):
        """Создает именованный временный файл в временной директории.

        Args:
            file_name (str): Имя файла.

        Returns:
            str: Путь к временному файлу.
        """
        file_path = os.path.join(self.temp_dir, file_name)
        open(file_path, 'w').close()
        self.temp_files.append(file_path)
        return file_path

    def create_temp_dir(self, dir_name):
        """Создает временную директорию.

        Args:
            dir_name (str): Имя директории.

        Returns:
            str: Путь к временной директории.
        """
        dir_path = os.path.join(os.getcwd(), dir_name)
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        self.temp_dirs.append(dir_path)
        return dir_path

    def cleanup(self):
        """Удаляет все зарегистрированные временные файлы и директории."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Ошибка удаления директории: {e}")

    def rm_file(self, file_name):
        os.remove(os.path.join(self.temp_dir, file_name))
        self.temp_files.remove(file_name)
