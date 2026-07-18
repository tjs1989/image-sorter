# Google Drive upload (`pushmedia`)

Mirrors a locally sorted folder tree into a personal Google Drive over user
OAuth. A service account is deliberately not used: it has no storage quota on a
consumer Drive.

## One-time setup

1. Install the runtime deps (adds PyDrive2):
   ```bash
   pip install -r requirements.txt
   ```
2. In the [Google Cloud Console](https://console.cloud.google.com/):
   - Create a project (or reuse one) and enable the **Google Drive API**.
   - Create an **OAuth client ID** of type **Desktop app**.
   - Download it and save it as `client_secrets.json` in the repo root.
     (Path is configurable via `google_drive.client_secrets_path` in
     `config/system_config.yaml`. Both `client_secrets.json` and the cached
     `drive_token.json` are gitignored.)

That's it. There is no separate login command: the first `pushmedia` opens a
browser once to authorize, caches a refresh token in `drive_token.json`, and
runs headless (silent token refresh) from then on.

## Usage

```bash
python main.py pushmedia -f=/abs/local/sorted/path -r=Backup/Photos
```

- `-f` is the local folder to upload (absolute path).
- `-r` is the destination folder in My Drive; the local subtree is recreated
  underneath it.

Re-running is safe: folders are reused and files already present are skipped
(dedup is by name within a parent, not by content hash), so you can top up an
existing Drive folder incrementally after each `sort`. Hidden files and dirs
(`.DS_Store` and friends) are never uploaded.

## Scope

`config.google_drive.scope` defaults to full `https://www.googleapis.com/auth/drive`.
Full scope is required to reuse folders you created in the Drive web UI: with the
narrower `drive.file` scope an app can only see files it created, so it cannot
find your hand-made folders and would create same-named duplicates alongside
them. Narrow it to `drive.file` only if you let the app own an isolated folder
rather than topping up a hand-curated tree.
