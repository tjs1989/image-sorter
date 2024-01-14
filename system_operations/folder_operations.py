import logging
import os
from pathlib import Path


class FolderOperations:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def create_filepath(self, filepath):
        Path(filepath).mkdir(parents=True, exist_ok=True)

    def move_file_to_folder(self, current_path, new_path):
        os.rename(current_path, new_path)
