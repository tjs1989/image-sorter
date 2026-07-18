import logging
import os

from config.setup import resolve_path


class DriveAuth:
    """User-OAuth against a personal Google Drive.

    The first ``authorize`` opens a browser once for consent and caches a
    refresh token; subsequent calls load that token and refresh it silently,
    so uploads run headless. A service account is deliberately not used: it has
    no storage quota on a consumer Drive.
    """

    def __init__(self, client_secrets_path, token_path, scope):
        self.client_secrets_path = resolve_path(client_secrets_path)
        self.token_path = resolve_path(token_path)
        self.scope = scope

    def _build_gauth(self):
        # Lazy import so the app and tests load without PyDrive2 installed.
        from pydrive2.auth import GoogleAuth

        settings = {
            "client_config_backend": "file",
            "client_config_file": self.client_secrets_path,
            "get_refresh_token": True,
            "oauth_scope": [self.scope],
        }
        gauth = GoogleAuth(settings=settings)
        if os.path.exists(self.token_path):
            gauth.LoadCredentialsFile(self.token_path)
        return gauth

    def authorize(self):
        gauth = self._build_gauth()

        if gauth.credentials is None:
            logging.info("No cached credentials; opening a browser for one-time login")
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            logging.info("Refreshing expired Google Drive token")
            gauth.Refresh()
        else:
            gauth.Authorize()

        gauth.SaveCredentialsFile(self.token_path)
        return gauth


class DriveOperations:
    """Thin wrapper over PyDrive2 that mirrors a local tree into My Drive.

    Folder and file creation are deduplicated by title within a parent, so
    re-running after another sort reuses existing folders and skips files that
    are already uploaded rather than creating duplicates.
    """

    ROOT = "root"

    def __init__(self, drive):
        self.drive = drive
        # Folder ids by full path, so a tree of files sharing ancestor
        # directories resolves each directory with a single ListFile call.
        self._dir_ids = {}

    @classmethod
    def from_gauth(cls, gauth):
        from pydrive2.drive import GoogleDrive

        return cls(GoogleDrive(gauth))

    def _find(self, name, parent_id):
        safe_name = name.replace("'", "\\'")
        query = {
            "q": f"title = '{safe_name}' and '{parent_id}' in parents "
            "and trashed = false"
        }
        entries = self.drive.ListFile(query).GetList()
        return entries[0]["id"] if entries else None

    def create_leaf(self, path):
        """Ensure every segment of ``path`` exists; return the leaf folder id."""
        parent = self.ROOT
        accumulated = ""
        for segment in path.split("/"):
            if not segment:
                continue
            accumulated = f"{accumulated}/{segment}" if accumulated else segment
            if accumulated not in self._dir_ids:
                self._dir_ids[accumulated] = self.create_dir(segment, parent)
            parent = self._dir_ids[accumulated]
        return parent

    def create_dir(self, name, parent_id):
        existing = self._find(name, parent_id)
        if existing:
            logging.debug(f"Folder exists, reusing: {name}")
            return existing
        meta = {
            "title": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [{"id": parent_id}],
        }
        folder = self.drive.CreateFile(meta)
        folder.Upload()
        return folder["id"]

    def create_file(self, local_path, name, parent_id):
        if self._find(name, parent_id):
            logging.info(f"Already in Drive, skipping: {name}")
            return False
        meta = {"title": name, "parents": [{"id": parent_id}]}
        drive_file = self.drive.CreateFile(meta)
        drive_file.SetContentFile(local_path)
        drive_file.Upload()
        return True
