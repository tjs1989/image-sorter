from system_operations.file_operations import FileOperations


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


def test_recurses_into_subfolders(tmp_path):
    _touch(tmp_path / "DCIM" / "Camera" / "IMG_1.jpg")
    _touch(tmp_path / "Pictures" / "Screenshots" / "shot.png")
    _touch(tmp_path / "loose.jpeg")

    files = FileOperations(str(tmp_path)).get_list_of_files_in_path_by_type(
        [".jpg", ".png", ".jpeg"]
    )

    names = sorted(p.rsplit("/", 1)[-1] for p in files)
    assert names == ["IMG_1.jpg", "loose.jpeg", "shot.png"]


def test_extension_match_is_case_insensitive(tmp_path):
    _touch(tmp_path / "a.JPG")
    _touch(tmp_path / "b.Png")

    files = FileOperations(str(tmp_path)).get_list_of_files_in_path_by_type(
        [".jpg", ".png"]
    )

    assert len(files) == 2


def test_excludes_top_level_dirs(tmp_path):
    _touch(tmp_path / "Images" / "2024" / "already_sorted.jpg")
    _touch(tmp_path / "DCIM" / "fresh.jpg")

    files = FileOperations(str(tmp_path)).get_list_of_files_in_path_by_type(
        [".jpg"], exclude_top_level_dirs=["Images", "Videos", "Audio"]
    )

    assert len(files) == 1
    assert files[0].endswith("fresh.jpg")


def test_no_matching_files_returns_empty(tmp_path):
    _touch(tmp_path / "readme.txt")
    files = FileOperations(str(tmp_path)).get_list_of_files_in_path_by_type([".jpg"])
    assert files == []


def test_filters_extensions_not_in_list(tmp_path):
    _touch(tmp_path / "a.jpg")
    _touch(tmp_path / "b.txt")
    _touch(tmp_path / "c.mp4")

    files = FileOperations(str(tmp_path)).get_list_of_files_in_path_by_type([".jpg"])

    assert len(files) == 1
    assert files[0].endswith("a.jpg")
