import glob
import os
from datetime import datetime
import file_format_config


class FileOperations:
    def __init__(self, files_path):
        self.files_path = files_path

    def get_file_last_modified_details(self, full_file_path):
        modified_time = os.stat(full_file_path).st_mtime
        modified_datetime = datetime.fromtimestamp(modified_time)

        file_details = {
            "modified_year": modified_datetime.strftime("%Y"),
            "modified_date": modified_datetime.strftime("%d-%m-%y"),
            "modified_month": modified_datetime.strftime("%B")
        }
        return file_details

    def get_list_of_files_in_path_by_type(self, file_extension_types):
        file_list = []

        for file_extension in file_extension_types:
            file_list.append(glob.glob(f"{self.files_path}/*{file_extension}"))

        return [file for files in file_list for file in files]

