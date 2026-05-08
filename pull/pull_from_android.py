import logging
import subprocess

from config.setup import get_system_config
from pull.adb_availability import AdbAvailability
from system_operations.folder_operations import FolderOperations


class PullFromAndroid:
    def __init__(self, destination_path):
        self.destination_path = destination_path
        self.system_config = get_system_config()
        self.folder_operations = FolderOperations(destination_path)
        self.adb_availability = AdbAvailability()

    def pull_folders(self):
        for remote_path in self.system_config["android_source_paths"]:
            logging.info(f"Pulling {remote_path} into {self.destination_path}")
            result = subprocess.run(
                ["adb", "pull", remote_path, self.destination_path],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logging.warning(
                    f"adb pull failed for {remote_path}: {result.stderr.strip()}"
                )
                continue
            if result.stdout.strip():
                logging.info(result.stdout.strip())

    def pull(self):
        self.adb_availability.verify()
        self.folder_operations.create_filepath(self.destination_path)
        self.pull_folders()
