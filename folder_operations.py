import logging
import os
from os import path


class FolderOperations:
    def __init__(self, image_folder_path):
        self.image_folder_path = image_folder_path

    def create_folder(self, folder_name):
        new_folder_path = f"{self.image_folder_path}/{folder_name}"
        os.mkdir(new_folder_path)
        logging.info(f"Created the folder {new_folder_path}")

    def does_folder_exist_in_image_path(self, folder_name):
        return path.exists(f"{self.image_folder_path}/{folder_name}")
