import file_format_config
import os


def create_year_and_month_structure_if_it_does_not_exist(file_details, file_type):
    year_folder_path = f"{file_type}/{file_details['modified_year']}"
    month_folder_path = f"{year_folder_path}/{file_details['modified_month']}"

    create_folder_if_it_does_not_exist(folder_name=year_folder_path)
    create_folder_if_it_does_not_exist(folder_name=month_folder_path)


def create_folder_if_it_does_not_exist(folder_name):
    if not folder_operations.does_folder_exist_in_path(folder_name):
        folder_operations.create_folder(folder_name=folder_name)


def process_files_in_file_list(list_of_files, file_type):
    for file in list_of_files:
        file_details = file_operations.get_file_last_modified_details(file)

        create_year_and_month_structure_if_it_does_not_exist(file_details=file_details, file_type=file_type)

        sorted_file_new_folder_path = f"{file_type}/" \
                                      f"{file_details['modified_year']}/" \
                                      f"{file_details['modified_month']}" \
                                      f"/{file_details['modified_date']}"

        create_folder_if_it_does_not_exist(folder_name=sorted_file_new_folder_path)

        folder_operations.move_file_to_folder(file_name=os.path.basename(file),
                                              new_folder_path=sorted_file_new_folder_path)

def put_images_into_folders(file_folder_path):
    file_operations = file_operations.FileOperations(file_folder_path)
    folder_operations = folder_operations.FolderOperations(file_folder_path)

    for file_type in file_format_config.supported_file_types.values():
        create_folder_if_it_does_not_exist(folder_name=file_type)

        file_list = file_operations.get_list_of_files_in_path_by_type(file_type=file_type)

        process_files_in_file_list(file_list, file_type=file_type)
