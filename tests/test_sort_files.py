import os
from datetime import datetime

from sort.sort_files import SortFiles


def _touch_with_mtime(path, dt):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    ts = dt.timestamp()
    os.utime(path, (ts, ts))


def test_sort_recurses_into_device_layout(tmp_path):
    captured = datetime(2024, 6, 15, 12, 0, 0)
    _touch_with_mtime(tmp_path / "DCIM" / "Camera" / "IMG_1.jpg", captured)
    _touch_with_mtime(tmp_path / "DCIM" / "Camera" / "VID_1.mp4", captured)
    _touch_with_mtime(tmp_path / "Pictures" / "Screenshots" / "shot.png", captured)
    _touch_with_mtime(tmp_path / "Music" / "song.mp3", captured)
    _touch_with_mtime(tmp_path / "loose.jpeg", captured)

    SortFiles(str(tmp_path)).sort_files_into_folders()

    images_day = tmp_path / "Images" / "2024" / "June" / "15-06-24"
    videos_day = tmp_path / "Videos" / "2024" / "June" / "15-06-24"
    audio_day = tmp_path / "Audio" / "2024" / "June" / "15-06-24"

    assert (images_day / "IMG_1.jpg").exists()
    assert (images_day / "shot.png").exists()
    assert (images_day / "loose.jpeg").exists()
    assert (videos_day / "VID_1.mp4").exists()
    assert (audio_day / "song.mp3").exists()

    assert not (tmp_path / "DCIM" / "Camera" / "IMG_1.jpg").exists()
    assert not (tmp_path / "loose.jpeg").exists()


def test_sort_groups_files_by_modified_date(tmp_path):
    jan = datetime(2023, 1, 5, 10, 0, 0)
    feb = datetime(2023, 2, 20, 10, 0, 0)
    _touch_with_mtime(tmp_path / "winter.jpg", jan)
    _touch_with_mtime(tmp_path / "spring.jpg", feb)

    SortFiles(str(tmp_path)).sort_files_into_folders()

    assert (tmp_path / "Images" / "2023" / "January" / "05-01-23" / "winter.jpg").exists()
    assert (tmp_path / "Images" / "2023" / "February" / "20-02-23" / "spring.jpg").exists()


def test_sort_is_idempotent_when_rerun(tmp_path):
    captured = datetime(2024, 6, 15, 12, 0, 0)
    _touch_with_mtime(tmp_path / "DCIM" / "img.jpg", captured)

    SortFiles(str(tmp_path)).sort_files_into_folders()
    SortFiles(str(tmp_path)).sort_files_into_folders()

    target_dir = tmp_path / "Images" / "2024" / "June" / "15-06-24"
    contents = list(target_dir.iterdir())
    assert len(contents) == 1
    assert contents[0].name == "img.jpg"
