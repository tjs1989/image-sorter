# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running

Python 3.11.6 (see `.python-version`). Runtime dependency is `pyyaml`; dev dependency is `pytest` (`pip install -r requirements-dev.txt`). No build script or linter configured.

```bash
pytest                                   # run the full test suite (config in pytest.ini)
pytest tests/test_pull_media.py          # run one file
pytest -k recurs                         # run tests matching a keyword
```

`pytest.ini` sets `pythonpath = .` so tests can import the project's top-level packages (`adb`, `sort`, `system_operations`, etc.) without any package install.

```bash
python main.py pullmedia       -f=/abs/path   # adb pull DCIM/Pictures/Movies/Music into folder
python main.py sort            -f=/abs/path   # sort into Type/Year/Month/Date (recursive)
python main.py delete          -f=/abs/path   # delete files <1MB, then prune empty dirs
python main.py purgemedia                     # delete all media on the device (interactive confirm)
python main.py -d ...                         # add -d for DEBUG logging (default INFO)
```

`pullmedia` and `purgemedia` require `adb` on PATH (`brew install --cask android-platform-tools`) and a single authorized device. Source paths on the device are configured via `android_source_paths` in `system_config.yaml` and are shared by both commands.

The `-f` argument must be an **absolute** path; the script does not resolve relative paths. Logs are written to `debug.log` (truncated each run) and stdout.

## Architecture

Three-layer CLI app:

1. **`main.py`** — argparse entry point using a `@subcommand([argument(...)])` decorator pattern (adapted from a Mike DePalatis blog post). The decorated function's `__name__` becomes the subcommand name, so `def sort(args)` registers as `python main.py sort`. To add a new top-level command, add a `@subcommand` function in `main.py` — do not edit a registry elsewhere.
2. **Command classes** — `sort/sort_files.py::SortFiles`, `delete/delete_files.py::DeleteFiles`, `adb/pull_media.py::PullMedia`, and `adb/purge_media.py::PurgeMedia`. Each takes a folder path (except `PurgeMedia`, whose target is the device), instantiates its own `FileOperations`/`FolderOperations` where needed, and exposes a small public API the CLI calls.
3. **`system_operations/`** — thin wrappers over `os`, `glob`, and `pathlib` for file/folder primitives (move, mkdir, walk, stat-based modified-date extraction, delete).

`utils/load_files.py` lowercases all top-level YAML keys on load via `get_yaml_keys`, so config access in code is always `self.system_config['lowercase_key']` even if the YAML uses a different case.

## Configuration is data, not code

`config/system_config.yaml` is the single source of truth for:

- Recognised file extensions per media type (`image_file_extensions`, `video_file_extensions`, `audio_file_extensions`)
- Initial folder names created at sort time (`initial_folder_structure`: `Images`, `Videos`, `Audio`)
- Date format strings used to build the `Year/Month/Date` directory tree
- The 1MB threshold for `delete` (`one_megabyte_in_bytes`)
- Log file name and log formatting

Adding a new image format, changing the delete threshold, or renaming the top-level folders is a YAML edit, **not** a code change. The string keys (e.g. `"Images"`) passed to `SortFiles.process_files_in_file_list` must match the entries in `initial_folder_structure`.

## Behavioural details worth knowing

- **Sort uses `mtime`, not EXIF.** `FileOperations.get_file_last_modified_details` reads `os.stat(...).st_mtime`. Files copied/restored from backups will sort by the copy date, not the photo date. `pullmedia` runs `adb pull -a`, where `-a` is what preserves the on-device mtime — without it the local copy gets the pull-time as its mtime and `sort` would group everything under the pull date.
- **Sort recurses but skips its own output dirs.** `get_list_of_files_in_path_by_type` walks subdirectories so files pulled into `DCIM/Camera/`, `Pictures/Screenshots/`, etc. are picked up. The top-level `Images/Videos/Audio/` folders (from `initial_folder_structure`) are pruned from the walk so re-runs don't re-process already-sorted output. Extension match is case-insensitive (`.JPG` works).
- **Delete is recursive and only operates on already-sorted trees.** `DeleteFiles` walks the whole tree via `FolderOperations.locate_folders_with_files`, so it's intended to run after a `sort`.
- **Hidden-file quirk in `folder_operations.py`.** `locate_folders_with_files` and `get_files_in_folder` skip a folder entirely if its **first** file (per `os.walk` ordering) starts with `.` — e.g. a single `.DS_Store` can hide all sibling files from the delete pass. Be aware before "fixing" this; it's load-bearing for ignoring macOS metadata folders.
- **`empty-folder removal is not recursive.`** `remove_folder` calls `os.rmdir`, which fails on non-empty directories — only leaf folders that became empty after deletion are removed.
- **`purgemedia` is on-device, irreversible, and gated by a typed token.** It runs `adb shell find <path> -mindepth 1 -delete` for every entry in `android_source_paths` (so the top-level `DCIM/`, `Pictures/`, etc. survive but their contents go) and then triggers a MediaStore rescan via `adb shell content call --uri content://media --method scan_volume --extra name:s:external_primary` so Gallery doesn't show ghost thumbnails. The user must type `confirm` (case-sensitive, stripped) — anything else aborts. There is intentionally no local-copy verification: backup is assumed to happen out-of-band (e.g. Google Drive after a `sort`).
