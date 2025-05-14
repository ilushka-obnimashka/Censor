import os
import shutil

import traceback


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances.keys():
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class TempFilesManager:
    """
    Manager for temporary files and directories.

    Implements the Singleton pattern. Automatically tracks and deletes created
    temporary files and directories when cleanup() is called.

    :ivar temp_files: List of paths to temporary files.
    :ivar temp_dirs: List of paths to temporary directories.
    """

    def __init__(self):
        """
        Initializes the temporary file manager.

        Creates a temporary directory for storing temporary files.
        """
        self.temp_files = []
        self.temp_dirs = []
        self.temp_dir = self.create_temp_dir("temp_files")

    def create_temp_file(self, file_name: str) -> str:
        """
        Creates a named temporary file in the temporary directory.

        :param file_name: The name of the file.
        :return: The path to the temporary file.
        """
        file_path = os.path.join(self.temp_dir, file_name)
        open(file_path, 'w').close()
        self.temp_files.append(file_path)
        return file_path

    def create_temp_dir(self, dir_name: str) -> str:
        """
        Creates a temporary directory.

        :param dir_name: The name of the directory.
        :return: The path to the temporary directory.
        """
        dir_path = os.path.join(os.getcwd(), dir_name)
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        self.temp_dirs.append(dir_path)
        return dir_path

    def cleanup(self) -> None:
        """
        Deletes all registered temporary files and directories.

        :raises Exception: If an error occurs while deleting the directory.
        """
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error deleting directory: {traceback.format_exc()}")

    def rm_file(self, file_name: str) -> None:
        """
        Deletes a temporary file from the temporary directory.

        :param file_name: The name of the file to delete.
        :raises FileNotFoundError: If the file is not found.
        """
        try:
            os.remove(os.path.join(self.temp_dir, file_name))
            self.temp_files.remove(os.path.join(self.temp_dir, file_name))
        except ValueError:
            print(f"File {file_name} not found in the list of temporary files.")
