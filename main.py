import glob
import logging
import os
import time
from datetime import datetime

from image_operations import get_list_of_images_in_path
import image_operations
import folder_operations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


def create_year_and_month_structure_if_it_does_not_exist(image_details):
    create_folder_if_it_does_not_exist(folder_name=image_details['modified_year'])

    create_folder_if_it_does_not_exist(
        folder_name=f"{image_details['modified_year']}/{image_details['modified_month']}"
    )


def create_folder_if_it_does_not_exist(folder_name):
    if not folder_operations.does_folder_exist_in_image_path(folder_name):
        folder_operations.create_folder(folder_name=folder_name)


if __name__ == '__main__':

    create_time = os.stat("/Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg").st_mtime
    modified_datetime = datetime.fromtimestamp(create_time)

    image_folder_path = "/Users/tonyskinner/Documents/phoneImages"

    image_operations = image_operations.ImageOperations(image_folder_path)
    folder_operations = folder_operations.FolderOperations(image_folder_path)

    image_list = get_list_of_images_in_path(image_folder_path)

    for image in image_list:
        image_details = image_operations.get_image_last_modified_details(image)

        create_year_and_month_structure_if_it_does_not_exist(image_details)

        image_new_folder_path = f"{image_details['modified_year']}/{image_details['modified_month']}" \
                                f"/{image_details['modified_date']}"

        create_folder_if_it_does_not_exist(folder_name=image_new_folder_path)

        folder_operations.move_file_to_folder(file_name=os.path.basename(image), new_folder_path=image_new_folder_path)


