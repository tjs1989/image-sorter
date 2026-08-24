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

    def locate_files_to_delete(self, size_in_bytes, file_extensions):
        deletable_extensions = {extension.lower() for extension in file_extensions}

        files = itertools.chain.from_iterable(
            self.folders_with_files[directory]['files_with_path'] for directory in self.folders_with_files)

        return [file for file in files
                if os.path.splitext(file)[1].lower() in deletable_extensions
                and os.path.getsize(file) < size_in_bytes]

    def remove_empty_post_delete_folders(self):
        for folder in self.folders_with_files:
            updated_folder_files = self.folder_operations.get_files_in_folder(folder)

            if len(updated_folder_files) == 0:
                self.folder_operations.remove_folder(folder)
                logging.info(f"Removed the folder {folder} because it is now empty")

    def delete_files_less_than_desired_size(self):
        delete_below_size = self.system_config['delete_below_size']
        size_in_bytes = delete_below_size['size_in_bytes']
        files_to_delete = self.locate_files_to_delete(size_in_bytes, delete_below_size['file_extensions'])

        for file in files_to_delete:
            self.file_operations.delete_file(file)
            logging.info(f"Removed the file {file} because it is under {size_in_bytes} bytes")
