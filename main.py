import logging
from system_operations import folder_operations, file_operations
import file_format_config
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)



def clear_log_file():
    file = open("debug.log", "r+")
    file.truncate(0)
    file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--media', help="The full path to the folder where your media is located", required=True)
    args = parser.parse_args()
    file_folder_path = args.media

    clear_log_file()
