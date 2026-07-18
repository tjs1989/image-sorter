import os

from config.setup import resolve_path

SETUP_HELP = (
    "Google Drive is not set up yet. One-time steps:\n"
    "  1. In Google Cloud Console: create a project, enable the Drive API, and\n"
    "     create an OAuth client ID of type 'Desktop app'.\n"
    "  2. Download it as 'client_secrets.json' into the repo root (or set\n"
    "     google_drive.client_secrets_path in config/system_config.yaml).\n"
    "  Then run pushmedia; a browser opens once to authorize, headless after."
)


class DriveAvailability:
    def __init__(self, client_secrets_path):
        self.client_secrets_path = resolve_path(client_secrets_path)

    def verify(self):
        try:
            import pydrive2  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "PyDrive2 not installed. Run: pip install -r requirements.txt"
            ) from exc

        if not os.path.exists(self.client_secrets_path):
            raise RuntimeError(
                f"OAuth client secrets not found at {self.client_secrets_path}.\n"
                f"{SETUP_HELP}"
            )
