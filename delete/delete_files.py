import itertools

import logging
import os.path

from system_operations.folder_operations import FolderOperations
from system_operations.file_operations import FileOperations
from config.setup import get_system_config


class DeleteFiles:
    def __init__(self, given_path):
        self.given_path = given_path
        self.system_config = get_system_config()
        self.folder_operations = FolderOperations(self.given_path)
        self.file_operations = FileOperations(self.given_path)
        self.folders_with_files = self.folder_operations.locate_folders_with_files()

    def locate_files_less_than_given_size(self, comparative_file_size):
        files_less_than_desired_size = []

        files = list(itertools.chain.from_iterable(
            self.folders_with_files[directory]['files_with_path'] for directory in self.folders_with_files))

        for file in files:
            file_size = os.path.getsize(file)
            if file_size < comparative_file_size:
                files_less_than_desired_size.append(file)

        return files_less_than_desired_size

    def delete_files_less_than_desired_size(self):
        files_to_delete = self.locate_files_less_than_given_size(self.system_config['one_megabyte_in_bytes'])

        for file in files_to_delete:
            self.file_operations.delete_file(file)
            logging.info(f"Removed the file {file}")

    def remove_empty_post_delete_folders(self):
        for folder in self.folders_with_files():
            updated_folder_files = self.folder_operations.get_files_in_folder(folder)

            if len(updated_folder_files) == 0:
                self.folder_operations.remove_folder(folder)
                logging.info(f"Removed the folder {folder} because it is now empty")
