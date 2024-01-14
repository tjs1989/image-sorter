import logging
import os

from system_operations import file_operations
from system_operations import folder_operations
from config import setup
from pathlib import Path


class SortFiles:
    def __init__(self, filepath):
        self.filepath = filepath
        self.system_config = setup.get_system_config()
        self.file_operations = file_operations.FileOperations(filepath)
        self.folder_operations = folder_operations.FolderOperations(filepath)

    def create_initial_folder_structure(self):
        for folder_name in self.system_config['initial_folder_structure']:
            new_folder_filepath = f"{self.filepath}/{folder_name}"
            self.folder_operations.create_filepath(new_folder_filepath)
            logging.info(f"Created the folder {new_folder_filepath} if it does not already exist")

    def process_files_in_file_list(self, list_of_files, file_type):
        for file in list_of_files:
            file_name = os.path.basename(file)
            file_details = self.file_operations.get_file_last_modified_details(file)

            new_file_folder_path = f"{self.filepath}/" \
                                   f"{file_type}/" \
                                   f"{file_details['modified_year']}/" \
                                   f"{file_details['modified_month']}" \
                                   f"/{file_details['modified_date']}"

            self.folder_operations.create_filepath(new_file_folder_path)
            logging.info(f"Creating the path {new_file_folder_path} if it does not exist")

            current_file_folder_path = f"{self.filepath}/{file_name}"

            print(current_file_folder_path)
            print(new_file_folder_path)
            quit()

            self.folder_operations.move_file_to_folder(current_path=current_file_folder_path,
                                                       new_path=new_file_folder_path)

            logging.info(f"Moved {file_name} to {new_file_folder_path}")

    def sort_files_into_folders(self):
        self.create_initial_folder_structure()

        image_files_list = self.file_operations.get_list_of_files_in_path_by_type(
            file_extension_types=self.system_config['image_file_extensions'])

        video_files_list = self.file_operations.get_list_of_files_in_path_by_type(
            file_extension_types=self.system_config['video_file_extensions'])

        audio_files_list = self.file_operations.get_list_of_files_in_path_by_type(
            file_extension_types=self.system_config['audio_file_extensions'])

        self.process_files_in_file_list(image_files_list, "Images")
        self.process_files_in_file_list(video_files_list, "Videos")
        self.process_files_in_file_list(audio_files_list, "Audio")
