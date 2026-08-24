import logging
import os

from system_operations import file_operations
from system_operations import folder_operations
from config import setup


class SortFiles:
    def __init__(self, filepath, phone_type):
        self.filepath = filepath
        self.phone_type = phone_type
        self.system_config = setup.get_system_config()
        self.initial_folder_structure = self.system_config['initial_folder_structure']
        self.file_operations = file_operations.FileOperations(filepath)
        self.folder_operations = folder_operations.FolderOperations(filepath)

    def create_initial_folder_structure(self):
        for folder_name in self.initial_folder_structure:
            new_folder_filepath = f"{self.filepath}/{folder_name}"
            self.folder_operations.create_filepath(new_folder_filepath)
            logging.info(f"Created the folder {new_folder_filepath} if it does not already exist")

    def discard_unwanted_files(self):
        discard_extensions = self.system_config['discard_file_extensions'].get(self.phone_type, [])

        files_to_discard = self.file_operations.get_list_of_files_in_path_by_type(
            file_extension_types=discard_extensions,
            exclude_top_level_dirs=self.initial_folder_structure)

        for file in files_to_discard:
            self.file_operations.delete_file(file)
            logging.info(f"Discarded {file} because its extension is in the {self.phone_type} discard list")

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

            self.folder_operations.move_file_to_folder(current_path=file,
                                                       new_path=f"{new_file_folder_path}/{file_name}")

            logging.info(f"Moved {file_name} to {new_file_folder_path}")

    def sort_files_into_folders(self):
        self.discard_unwanted_files()

        self.create_initial_folder_structure()

        image_files_list = self.file_operations.get_list_of_files_in_path_by_type(
            file_extension_types=self.system_config['image_file_extensions'],
            exclude_top_level_dirs=self.initial_folder_structure)

        video_files_list = self.file_operations.get_list_of_files_in_path_by_type(
            file_extension_types=self.system_config['video_file_extensions'],
            exclude_top_level_dirs=self.initial_folder_structure)

        audio_files_list = self.file_operations.get_list_of_files_in_path_by_type(
            file_extension_types=self.system_config['audio_file_extensions'],
            exclude_top_level_dirs=self.initial_folder_structure)

        self.process_files_in_file_list(image_files_list, "Images")
        self.process_files_in_file_list(video_files_list, "Videos")
        self.process_files_in_file_list(audio_files_list, "Audio")
