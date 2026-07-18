import os
from unittest.mock import MagicMock, patch

import pytest

from drive.push_media import PushMedia
from drive.auth import DriveOperations


@pytest.fixture
def pusher(tmp_path):
    return PushMedia(str(tmp_path), "Backup/Photos")


def _make_file(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write("x")


def test_iter_files_mirrors_local_tree_under_remote_path(pusher, tmp_path):
    _make_file(os.path.join(tmp_path, "Images", "2026", "July", "a.jpg"))
    _make_file(os.path.join(tmp_path, "Videos", "b.mp4"))

    mapping = dict(pusher._iter_files())

    assert mapping == {
        os.path.join(str(tmp_path), "Images", "2026", "July", "a.jpg"):
            "Backup/Photos/Images/2026/July/a.jpg",
        os.path.join(str(tmp_path), "Videos", "b.mp4"):
            "Backup/Photos/Videos/b.mp4",
    }


def test_iter_files_skips_hidden_files_and_dirs(pusher, tmp_path):
    _make_file(os.path.join(tmp_path, "Images", "a.jpg"))
    _make_file(os.path.join(tmp_path, "Images", ".DS_Store"))
    _make_file(os.path.join(tmp_path, ".Trash", "old.jpg"))

    remotes = [remote for _, remote in pusher._iter_files()]

    assert remotes == ["Backup/Photos/Images/a.jpg"]


def test_iter_files_without_remote_path_uses_bare_relative(tmp_path):
    pusher = PushMedia(str(tmp_path), "")
    _make_file(os.path.join(tmp_path, "Images", "a.jpg"))

    remotes = [remote for _, remote in pusher._iter_files()]

    assert remotes == ["Images/a.jpg"]


def test_upload_one_creates_path_then_file(pusher):
    pusher.operations = MagicMock()
    pusher.operations.create_leaf.return_value = "id2"

    pusher._upload_one("/local/a.jpg", "Backup/Photos/Images/a.jpg")

    pusher.operations.create_leaf.assert_called_once_with("Backup/Photos/Images")
    pusher.operations.create_file.assert_called_once_with(
        "/local/a.jpg", "a.jpg", "id2"
    )


def test_upload_tree_counts_new_and_skipped(pusher, tmp_path):
    _make_file(os.path.join(tmp_path, "a.jpg"))
    _make_file(os.path.join(tmp_path, "b.jpg"))
    pusher.operations = MagicMock()
    pusher.operations.create_path.return_value = ["root"]
    # First file uploaded (True), second already present (False).
    pusher.operations.create_file.side_effect = [True, False]

    seen, uploaded = pusher.upload_tree()

    assert (seen, uploaded) == (2, 1)


@patch.object(PushMedia, "upload_tree", return_value=(0, 0))
@patch.object(PushMedia, "_build_operations")
def test_push_orchestrates_verify_auth_then_upload(
    mock_build, mock_upload, pusher
):
    pusher.availability = MagicMock()

    pusher.push()

    pusher.availability.verify.assert_called_once()
    mock_build.assert_called_once()
    mock_upload.assert_called_once()


def _drive_returning(existing):
    """A fake PyDrive2 drive whose ListFile returns the given entries."""
    drive = MagicMock()
    drive.ListFile.return_value.GetList.return_value = existing
    return drive


def test_create_dir_reuses_existing_folder():
    drive = _drive_returning([{"id": "existing", "parents": [{"id": "root"}]}])
    ops = DriveOperations(drive)

    result = ops.create_dir("Images", "root")

    assert result == "existing"
    drive.CreateFile.assert_not_called()


def test_create_dir_creates_when_absent():
    drive = _drive_returning([])
    created = MagicMock()
    created.__getitem__.return_value = "new-id"
    drive.CreateFile.return_value = created
    ops = DriveOperations(drive)

    result = ops.create_dir("Images", "root")

    assert result == "new-id"
    created.Upload.assert_called_once()


def test_create_file_skips_when_already_present():
    drive = _drive_returning([{"id": "existing", "parents": [{"id": "p1"}]}])
    ops = DriveOperations(drive)

    result = ops.create_file("/local/a.jpg", "a.jpg", "p1")

    assert result is False
    drive.CreateFile.assert_not_called()


def test_create_file_uploads_when_absent():
    drive = _drive_returning([])
    new_file = MagicMock()
    drive.CreateFile.return_value = new_file
    ops = DriveOperations(drive)

    result = ops.create_file("/local/a.jpg", "a.jpg", "p1")

    assert result is True
    new_file.SetContentFile.assert_called_once_with("/local/a.jpg")
    new_file.Upload.assert_called_once()


def test_create_leaf_walks_segments_and_returns_leaf_id():
    drive = _drive_returning([])
    created = MagicMock()
    created.__getitem__.side_effect = ["id1", "id2"]
    drive.CreateFile.return_value = created
    ops = DriveOperations(drive)

    assert ops.create_leaf("Backup/Photos") == "id2"


def test_create_leaf_caches_resolved_dirs_across_calls():
    drive = _drive_returning([])
    created = MagicMock()
    created.__getitem__.side_effect = ["id1", "id2"]
    drive.CreateFile.return_value = created
    ops = DriveOperations(drive)

    ops.create_leaf("Backup/Photos")
    # Second call for the same tree must not hit the API again.
    drive.ListFile.reset_mock()
    drive.CreateFile.reset_mock()

    assert ops.create_leaf("Backup/Photos") == "id2"
    drive.ListFile.assert_not_called()
    drive.CreateFile.assert_not_called()
