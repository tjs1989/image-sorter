import glob
import os
import time
from datetime import datetime


class ImageOperations:
    def __init__(self, image_folder_path):
        self.image_folder_path = image_folder_path

    def get_list_of_images_in_path(self):
        jpg_list = glob.glob(f"{self.image_folder_path}/*.jpg")
        gif_list = glob.glob(f"{self.image_folder_path}/*.gif")
        png_list = glob.glob(f"{self.image_folder_path}/*.png")
        return jpg_list + gif_list + png_list

    def get_image_last_modified_year(self, image_path):
        # gives the create time as a unix timestamp
        create_time = os.stat(image_path).st_mtime

        # returns a datetime object
        modified_datetime = datetime.fromtimestamp(create_time)

        # print the year
        return modified_datetime.strftime("%Y")

