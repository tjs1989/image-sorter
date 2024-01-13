import logging
import os
from os import path


class FolderOperations:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def create_folder(self, folder_name):
        new_folder_path = f"{self.folder_path}/{folder_name}"
        os.mkdir(new_folder_path)
        logging.info(f"Created the folder {new_folder_path}")

    def does_folder_exist_in_path(self, folder_name):
        return path.exists(f"{self.folder_path}/{folder_name}")

    def move_file_to_folder(self, file_name, new_folder_path):
        current_path = f"{self.folder_path}/{file_name}"
        new_path = f"{self.folder_path}/{new_folder_path}/{file_name}"

        os.rename(current_path, new_path)
        logging.info(f"Moved {file_name} to {new_folder_path}")
