import os
from pathlib import Path


class FolderOperations:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def create_filepath(self, filepath):
        Path(filepath).mkdir(parents=True, exist_ok=True)

    def move_file_to_folder(self, current_path, new_path):
        os.rename(current_path, new_path)

    def locate_folders_with_files(self):
        folders_with_files = {}

        for root, dirs, files in os.walk(self.folder_path):
            if files[0][0] == '.':
                continue

            for x in range(0, len(files)):
                files[x] = f"{root}/{files[x]}"

            folders_with_files[root] = {
                "files_with_path": files
            }

        return folders_with_files

    @staticmethod
    def get_files_in_folder(path):
        return [files for _, _, files in os.walk(path) if not files[0][0] == '.']

    @staticmethod
    def remove_folder(path):
        os.rmdir(path)
