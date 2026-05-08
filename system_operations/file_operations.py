import os
from datetime import datetime
from config.setup import get_system_config


class FileOperations:
    def __init__(self, files_path):
        self.files_path = files_path
        self.system_config = get_system_config()

    def get_file_last_modified_details(self, full_file_path):
        modified_time = os.stat(full_file_path).st_mtime
        modified_datetime = datetime.fromtimestamp(modified_time)

        file_details = {
            "modified_year": modified_datetime.strftime(self.system_config['date_time_formats']['year']),
            "modified_date": modified_datetime.strftime(self.system_config['date_time_formats']['dmy_dashes']),
            "modified_month": modified_datetime.strftime(self.system_config['date_time_formats']['full_month_name'])
        }

        return file_details

    def get_list_of_files_in_path_by_type(self, file_extension_types, exclude_top_level_dirs=None):
        excluded = set(exclude_top_level_dirs or [])
        extensions = tuple(ext.lower() for ext in file_extension_types)

        matches = []
        for root, dirs, files in os.walk(self.files_path):
            if root == self.files_path and excluded:
                dirs[:] = [d for d in dirs if d not in excluded]
            for name in files:
                if name.lower().endswith(extensions):
                    matches.append(os.path.join(root, name))
        return matches

    @staticmethod
    def delete_file(filepath):
        os.remove(filepath)


