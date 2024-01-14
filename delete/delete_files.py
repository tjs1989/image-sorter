import itertools
import json
import os.path

from system_operations.folder_operations import FolderOperations
from config.setup import get_system_config


class DeleteFiles:
    def __init__(self, given_path):
        self.given_path = given_path
        self.system_config = get_system_config()
        self.folder_operations = FolderOperations(self.given_path)
        self.directories_with_files = self.folder_operations.locate_folders_with_files()

    def locate_files_less_than_given_size(self, comparative_file_size):
        files_less_than_desired_size = []

        files = list(itertools.chain.from_iterable(
            self.directories_with_files[directory]['files_with_path'] for directory in self.directories_with_files))

        for file in files:
            file_size = os.path.getsize(file)
            if file_size < comparative_file_size:
                files_less_than_desired_size.append(file)

        return files_less_than_desired_size

    def locate_and_delete_files(self):
        files_to_delete = self.locate_files_less_than_given_size(self.system_config['one_megabyte_in_bytes'])
        print(files_to_delete)


