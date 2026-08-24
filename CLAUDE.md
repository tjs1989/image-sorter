# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

Python 3.11.6 (see `.python-version`). Runtime dependencies are `pyyaml` and `PyDrive2` (`pip install -r requirements.txt`); dev dependency is `pytest` (`pip install -r requirements-dev.txt`). No build script or linter configured. `PyDrive2` is only needed for the `pushmedia` command and is lazily imported, so the rest of the app and the test suite run without it installed.

```bash
pytest                                   # run the full test suite (config in pytest.ini)
pytest tests/test_pull_media.py          # run one file
pytest -k recurs                         # run tests matching a keyword
```

`pytest.ini` sets `pythonpath = .` so tests can import the project's top-level packages (`adb`, `sort`, `system_operations`, etc.) without any package install.

```bash
python main.py pullmedia       -f=/abs/path   # adb pull DCIM/Pictures/Movies/Music into folder
python main.py sort            -f=/abs/path   # sort into Type/Year/Month/Date (recursive)
python main.py sort -f=/abs/path -p=iphone    # same, but discard the phone-specific junk first (-p optional)
python main.py delete          -f=/abs/path   # delete files <1MB, then prune empty dirs
python main.py purgemedia                     # delete all media on the device (interactive confirm)
python main.py pushmedia -f=/abs/path -r=Dir   # mirror a sorted folder tree into Google Drive
python main.py -d ...                         # add -d for DEBUG logging (default INFO)
```

`pushmedia` uploads a sorted tree to a personal Google Drive over user OAuth (no service account, which has no storage quota on a consumer Drive). One-time setup lives in `drive/README.md`: create a Google Cloud project, enable the Drive API, create an OAuth client ID of type "Desktop app", download it as `client_secrets.json` in the repo root. There is no separate login command: the first `pushmedia` opens a browser once to authorize, caches a refresh token in `drive_token.json`, and runs headless (silent refresh) after. `pushmedia -f` is the local folder, `-r` is the destination folder in My Drive; the local subtree is recreated under `-r`. Both `client_secrets.json` and `drive_token.json` are gitignored. See `config.google_drive` in `system_config.yaml` for paths and scope.

`pullmedia` and `purgemedia` require `adb` on PATH (`brew install --cask android-platform-tools`) and a single authorized device. `pullmedia` reads `android_source_paths` from `system_config.yaml`; `purgemedia` reads the union of `android_source_paths` and `android_purge_only_paths`. The split exists because some directories (e.g. WhatsApp's `/sdcard/Android/media/com.whatsapp/WhatsApp/Media`) hold media that's been re-encoded/compressed by the originating app and isn't worth backing up — but still wants clearing off the device.

The `-f` argument must be an **absolute** path; the script does not resolve relative paths. Logs are written to `debug.log` (truncated each run) and stdout.

## Architecture

Three-layer CLI app:

1. **`main.py`** — argparse entry point using a `@subcommand([argument(...)])` decorator pattern (adapted from a Mike DePalatis blog post). The decorated function's `__name__` becomes the subcommand name, so `def sort(args)` registers as `python main.py sort`. To add a new top-level command, add a `@subcommand` function in `main.py` — do not edit a registry elsewhere.
2. **Command classes** — `sort/sort_files.py::SortFiles`, `delete/delete_files.py::DeleteFiles`, `adb/pull_media.py::PullMedia`, `adb/purge_media.py::PurgeMedia`, and `drive/push_media.py::PushMedia`. Each takes a folder path (except `PurgeMedia`, whose target is the device), instantiates its own `FileOperations`/`FolderOperations` where needed, and exposes a small public API the CLI calls. The `drive/` package adds `DriveAuth`/`DriveOperations` (PyDrive2 user-OAuth wrapper in `drive/auth.py`) and `DriveAvailability` (`drive/availability.py`), mirroring the `adb/availability.py` pattern.
3. **`system_operations/`** — thin wrappers over `os`, `glob`, and `pathlib` for file/folder primitives (move, mkdir, walk, stat-based modified-date extraction, delete).

`utils/load_files.py` lowercases all top-level YAML keys on load via `get_yaml_keys`, so config access in code is always `self.system_config['lowercase_key']` even if the YAML uses a different case.

## Configuration is data, not code

`config/system_config.yaml` is the single source of truth for:

- Recognised file extensions per media type (`image_file_extensions`, `video_file_extensions`, `audio_file_extensions`)
- Extensions deleted rather than sorted, per phone type (`discard_file_extensions`)
- Initial folder names created at sort time (`initial_folder_structure`: `Images`, `Videos`, `Audio`)
- Date format strings used to build the `Year/Month/Date` directory tree
- The 1MB threshold for `delete` (`one_megabyte_in_bytes`)
- Log file name and log formatting

Adding a new image format, changing the delete threshold, or renaming the top-level folders is a YAML edit, **not** a code change. The string keys (e.g. `"Images"`) passed to `SortFiles.process_files_in_file_list` must match the entries in `initial_folder_structure`.

## Behavioural details worth knowing

- **Sort uses `mtime`, not EXIF.** `FileOperations.get_file_last_modified_details` reads `os.stat(...).st_mtime`. Files copied/restored from backups will sort by the copy date, not the photo date. `pullmedia` runs `adb pull -a`, where `-a` is what preserves the on-device mtime — without it the local copy gets the pull-time as its mtime and `sort` would group everything under the pull date.
- **`sort -p` discards junk before sorting, and it is irreversible.** `discard_unwanted_files` runs first and deletes every file whose extension is in `discard_file_extensions[<phone type>]`. `-p` is optional and has no default, so omitting it discards nothing and sort still only ever moves files. `-p iphone` deletes `.aae` sidecars, which hold iOS edit instructions and are meaningless off the phone (iOS keeps the edited render next to them as `IMG_Exxxx`). Each deletion is logged, because `debug.log` is the only record of what went. Adding a phone type or a junk extension is a YAML edit: `main.py` derives the accepted `-p` values from the `discard_file_extensions` keys alone, so a phone type only becomes a valid `-p` value once it has something to discard (there is deliberately no `android` entry, and `-p android` is rejected). An extension listed nowhere in the config is simply ignored and left in place, which is the safe default.
- **Sort recurses but skips its own output dirs.** `get_list_of_files_in_path_by_type` walks subdirectories so files pulled into `DCIM/Camera/`, `Pictures/Screenshots/`, etc. are picked up. The top-level `Images/Videos/Audio/` folders (from `initial_folder_structure`) are pruned from the walk so re-runs don't re-process already-sorted output. Extension match is case-insensitive (`.JPG` works). The discard pass uses the same exclusion, so a discarded extension that somehow sits inside `Images/` is left alone.
- **Delete is recursive and only operates on already-sorted trees.** `DeleteFiles` walks the whole tree via `FolderOperations.locate_folders_with_files`, so it's intended to run after a `sort`.
- **Hidden-file quirk in `folder_operations.py`.** `locate_folders_with_files` and `get_files_in_folder` skip a folder entirely if its **first** file (per `os.walk` ordering) starts with `.` — e.g. a single `.DS_Store` can hide all sibling files from the delete pass. Be aware before "fixing" this; it's load-bearing for ignoring macOS metadata folders.
- **`empty-folder removal is not recursive.`** `remove_folder` calls `os.rmdir`, which fails on non-empty directories — only leaf folders that became empty after deletion are removed.
- **`purgemedia` is on-device, irreversible, and gated by a typed token.** It runs `adb shell find <path> -mindepth 1 -delete` for every entry in `android_source_paths + android_purge_only_paths` (so the top-level `DCIM/`, `Pictures/`, etc. survive but their contents go) and then triggers a MediaStore rescan via `adb shell content call --uri content://media --method scan_volume --extra name:s:external_primary` so Gallery doesn't show ghost thumbnails. The user must type `confirm` (case-sensitive, stripped) — anything else aborts. There is intentionally no local-copy verification: backup is assumed to happen out-of-band (e.g. Google Drive after a `sort`).
- **`pushmedia` is idempotent and reuses existing Drive folders.** `PushMedia` walks the local `-f` tree with `os.walk` and recreates each subdirectory under the `-r` Drive folder. `DriveOperations` deduplicates by title-within-parent: folders are reused and files already present are skipped (logged, not re-uploaded), so re-running after another `sort` tops up incrementally without duplicating. Dedup is by name, not content hash, so a locally edited file that keeps its name is not re-uploaded. Hidden files and dirs (names starting with `.`) are skipped, so macOS metadata like `.DS_Store` is never uploaded.
- **Drive scope must be full `drive`, not `drive.file`, to reuse manually-created folders.** With the `drive.file` scope an app can only see files it created, so it cannot find folders you made in the Drive web UI and would create same-named duplicates alongside them. `config.google_drive.scope` therefore defaults to full `https://www.googleapis.com/auth/drive`. Narrow it to `drive.file` only if you let the app own an isolated folder rather than topping up a hand-curated tree.
- **Drive auth is user OAuth with a cached refresh token.** `DriveAuth` (`drive/auth.py`) opens a browser once on the first `pushmedia` (when no token is cached), then loads and silently refreshes `drive_token.json` on later runs so subsequent uploads are headless. There is no separate login command; `client_secrets.json` is the app identity (from Cloud Console) and `drive_token.json` is the user's cached grant (created after consent). `DriveAvailability.verify()` fails fast if `client_secrets.json` is missing. Secret/token paths in `config.google_drive` are resolved relative to the repo root (or absolute) via `config.setup.resolve_path`, independent of the current working directory.
