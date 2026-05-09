import logging
import subprocess

from config.setup import get_system_config
from adb.availability import Availability

CONFIRMATION_TOKEN = "confirm"

WARNING_BANNER = r"""
   ____  _   _ ____   ____ _____
  |  _ \| | | |  _ \ / ___| ____|
  | |_) | | | | |_) | |  _|  _|
  |  __/| |_| |  _ <| |_| | |___
  |_|    \___/|_| \_\\____|_____|
"""


class PurgeMedia:
    def __init__(self):
        self.system_config = get_system_config()
        self.availability = Availability()
        self.paths_to_purge = (
            self.system_config["android_source_paths"]
            + self.system_config.get("android_purge_only_paths", [])
        )

    def _show_warning(self):
        paths = "\n".join(f"    - {p}" for p in self.paths_to_purge)
        print(
            f"{WARNING_BANNER}\n"
            "  !!!  WARNING  !!!  WARNING  !!!  WARNING  !!!\n\n"
            "  This will PERMANENTLY DELETE all media in:\n"
            f"{paths}\n\n"
            "  on the connected Android device.\n"
            "  This action is IRREVERSIBLE.\n"
        )

    def _prompt_confirmation(self):
        response = input(
            f"  Type '{CONFIRMATION_TOKEN}' to proceed, anything else to abort: "
        )
        return response.strip() == CONFIRMATION_TOKEN

    def purge_folders(self):
        for remote_path in self.paths_to_purge:
            logging.info(f"Purging contents of {remote_path} on device")
            result = subprocess.run(
                ["adb", "shell", "find", remote_path, "-mindepth", "1", "-delete"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logging.warning(
                    f"adb purge failed for {remote_path}: {result.stderr.strip()}"
                )
                continue
            if result.stdout.strip():
                logging.info(result.stdout.strip())

    def trigger_media_rescan(self):
        logging.info("Triggering MediaStore rescan on external_primary volume")
        result = subprocess.run(
            [
                "adb", "shell",
                "content", "call",
                "--uri", "content://media",
                "--method", "scan_volume",
                "--extra", "name:s:external_primary",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logging.warning(f"Media rescan failed: {result.stderr.strip()}")

    def purge(self):
        self.availability.verify()
        self._show_warning()
        if not self._prompt_confirmation():
            logging.info("Purge aborted by user.")
            return
        self.purge_folders()
        self.trigger_media_rescan()
