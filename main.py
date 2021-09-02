import glob
import os
import time
from datetime import datetime

import image_operations
import image_operations

if __name__ == '__main__':

    # /Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg

    image_path = "/Users/tonyskinner/Documents/phoneImages"

    image_operations = image_operations.ImageOperations(image_path)


    # print("Last modified: %s" % time.ctime(os.path.getmtime("/Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg")))
    # print(time.ctime(os.path.getmtime("/Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg")))
    # print("Created: %s" % time.ctime(os.path.getctime("/Users/tonyskinner/Documents/phoneImages/IMG_20190201_070709.jpg")))

    image_list = image_operations.get_list_of_images_in_path()

    for image in image_list:
        print(image_operations.get_image_last_modified_year(image))


