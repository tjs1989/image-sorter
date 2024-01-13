import file_format_config
import os

from system_operations import file_operations
from system_operations import folder_operations


class SortImages:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file_operations = file_operations.FileOperations(filepath)
        self.folder_operations = folder_operations.FolderOperations(filepath)

    def create_year_and_month_structure_if_it_does_not_exist(self, file_details, file_type):
        year_folder_path = f"{file_type}/{file_details['modified_year']}"
        month_folder_path = f"{year_folder_path}/{file_details['modified_month']}"

        self.create_folder_if_it_does_not_exist(folder_name=year_folder_path)
        self.create_folder_if_it_does_not_exist(folder_name=month_folder_path)

    def create_folder_if_it_does_not_exist(self, folder_name):
        if not self.folder_operations.does_folder_exist_in_path(folder_name):
            self.folder_operations.create_folder(folder_name=folder_name)

    def process_files_in_file_list(self, list_of_files, file_type):
        for file in list_of_files:
            file_details = self.file_operations.get_file_last_modified_details(file)

            self.create_year_and_month_structure_if_it_does_not_exist(file_details=file_details, file_type=file_type)

            sorted_file_new_folder_path = f"{file_type}/" \
                                          f"{file_details['modified_year']}/" \
                                          f"{file_details['modified_month']}" \
                                          f"/{file_details['modified_date']}"

            self.create_folder_if_it_does_not_exist(folder_name=sorted_file_new_folder_path)

            self.folder_operations.move_file_to_folder(file_name=os.path.basename(file),
                                                       new_folder_path=sorted_file_new_folder_path)

    def put_images_into_folders(self, file_folder_path):

        for file_type in file_format_config.supported_file_types.values():
            self.create_folder_if_it_does_not_exist(folder_name=file_type)

            file_list = self.file_operations.get_list_of_files_in_path_by_type(file_type=file_type)

            self.process_files_in_file_list(file_list, file_type=file_type)
