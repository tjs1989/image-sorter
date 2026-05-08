import logging
import shutil
import subprocess

from config.setup import get_system_config
from system_operations.folder_operations import FolderOperations


class PullFromAndroid:
    def __init__(self, destination_path):
        self.destination_path = destination_path
        self.system_config = get_system_config()
        self.folder_operations = FolderOperations(destination_path)

    def verify_adb_available(self):
        if shutil.which("adb") is None:
            raise RuntimeError(
                "adb not found on PATH. Install with: "
                "brew install --cask android-platform-tools"
            )

        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, check=True
        )
        device_lines = result.stdout.splitlines()[1:]
        authorized = [line for line in device_lines if "\tdevice" in line]
        unauthorized = [line for line in device_lines if "\tunauthorized" in line]

        if unauthorized:
            raise RuntimeError(
                "Device connected but unauthorized. "
                "Accept the USB debugging prompt on the phone and re-run."
            )
        if not authorized:
            raise RuntimeError(
                "No authorized Android device detected. "
                "Connect via USB with USB debugging enabled."
            )
        if len(authorized) > 1:
            raise RuntimeError(
                "Multiple devices detected. Disconnect all but one."
            )

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
        self.verify_adb_available()
        self.folder_operations.create_filepath(self.destination_path)
        self.pull_folders()
