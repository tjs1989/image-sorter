import glob
import os
from datetime import datetime


def get_list_of_images_in_path(image_folder_path):
    jpg_list = glob.glob(f"{image_folder_path}/*.jpg")
    gif_list = glob.glob(f"{image_folder_path}/*.gif")
    png_list = glob.glob(f"{image_folder_path}/*.png")
    return jpg_list + gif_list + png_list


class ImageOperations:
    def __init__(self, image_path):
        self.image_path = image_path

    def get_image_last_modified_details(self, image_path):
        modified_time = os.stat(image_path).st_mtime
        modified_datetime = datetime.fromtimestamp(modified_time)

        image_details = {
            "modified_year": modified_datetime.strftime("%Y"),
            "modified_date": modified_datetime.strftime("%d-%m-%y"),
            "modified_month": modified_datetime.strftime("%B")
        }

        return image_details
