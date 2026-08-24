import logging
import os
import posixpath

from config.setup import get_system_config
from drive.availability import DriveAvailability
from drive.auth import DriveAuth, DriveOperations


def build_collaborators(system_config):
    google_drive = system_config["google_drive"]
    availability = DriveAvailability(google_drive["client_secrets_path"])
    auth = DriveAuth(
        google_drive["client_secrets_path"],
        google_drive["token_path"],
        google_drive["scope"],
    )
    return availability, auth


class PushMedia:
    """Mirror a locally sorted folder tree into a personal Google Drive.

    ``source_path`` is an absolute local folder (typically a sorted tree);
    ``remote_path`` is the destination folder in My Drive. The local
    subdirectory structure is recreated underneath ``remote_path``. Hidden
    files and folders (``.DS_Store`` and friends) are skipped.
    """

    def __init__(self, source_path, remote_path):
        self.source_path = source_path
        self.remote_path = remote_path.strip("/")
        self.availability, self.auth = build_collaborators(get_system_config())
        self.operations = None

    def _build_operations(self):
        gauth = self.auth.authorize()
        self.operations = DriveOperations.from_gauth(gauth)

    def _iter_files(self):
        for root, dirs, files in os.walk(self.source_path):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            for name in sorted(files):
                if name.startswith("."):
                    continue
                local = os.path.join(root, name)
                relative = os.path.relpath(local, self.source_path).replace(os.sep, "/")
                remote = (
                    posixpath.join(self.remote_path, relative)
                    if self.remote_path
                    else relative
                )
                yield local, remote

    def _upload_one(self, local_file, remote_file):
        remote_dir = posixpath.dirname(remote_file)
        parent_id = self.operations.create_leaf(remote_dir)
        name = posixpath.basename(remote_file)
        return self.operations.create_file(local_file, name, parent_id)

    def upload_tree(self):
        seen = 0
        uploaded = 0
        for local_file, remote_file in self._iter_files():
            seen += 1
            logging.info(f"Uploading {local_file} -> {remote_file}")
            if self._upload_one(local_file, remote_file):
                uploaded += 1
        return seen, uploaded

    def push(self):
        self.availability.verify()
        self._build_operations()
        seen, uploaded = self.upload_tree()
        logging.info(
            f"Upload complete: {uploaded} new, {seen - uploaded} skipped "
            f"({seen} file(s) total)"
        )
