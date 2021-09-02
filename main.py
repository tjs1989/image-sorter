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


def create_folder_if_it_does_not_exist(folder_name):
    if not folder_operations.does_folder_exist_in_image_path(folder_name):
        folder_operations.create_folder(folder_name=folder_name)


if __name__ == '__main__':

    create_time = os.stat("/Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg").st_mtime
    modified_datetime = datetime.fromtimestamp(create_time)

    image_folder_path = "/Users/tonyskinner/Documents/phoneImages"

    image_operations = image_operations.ImageOperations(image_folder_path)
    folder_operations = folder_operations.FolderOperations(image_folder_path)

    # print("Last modified: %s" % time.ctime(os.path.getmtime("/Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg")))
    # print(time.ctime(os.path.getmtime("/Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg")))
    # print("Created: %s" % time.ctime(os.path.getctime("/Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg")))

    image_list = get_list_of_images_in_path(image_folder_path)

    for image in image_list:
        image_details = image_operations.get_image_last_modified_details(image)

        create_folder_if_it_does_not_exist(folder_name=image_details['modified_year'])
