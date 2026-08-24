import os

from delete.delete_files import DeleteFiles


def _write(path, size_in_bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"0" * size_in_bytes)


def test_delete_removes_small_files_with_a_listed_extension(tmp_path):
    _write(tmp_path / "whatsapp.jpg", 200_000)
    _write(tmp_path / "sticker.gif", 50_000)
    _write(tmp_path / "forwarded.mp4", 400_000)

    DeleteFiles(str(tmp_path)).delete_files_less_than_desired_size()

    assert not (tmp_path / "whatsapp.jpg").exists()
    assert not (tmp_path / "sticker.gif").exists()
    assert not (tmp_path / "forwarded.mp4").exists()


def test_delete_leaves_small_camera_originals_alone(tmp_path):
    _write(tmp_path / "IMG_1.heic", 800_000)
    _write(tmp_path / "IMG_2.mov", 300_000)
    _write(tmp_path / "IMG_3.heif", 900_000)

    DeleteFiles(str(tmp_path)).delete_files_less_than_desired_size()

    assert (tmp_path / "IMG_1.heic").exists()
    assert (tmp_path / "IMG_2.mov").exists()
    assert (tmp_path / "IMG_3.heif").exists()


def test_delete_leaves_large_files_alone_even_with_a_listed_extension(tmp_path):
    _write(tmp_path / "real_photo.jpg", 2_000_000)

    DeleteFiles(str(tmp_path)).delete_files_less_than_desired_size()

    assert (tmp_path / "real_photo.jpg").exists()


def test_delete_matches_extensions_case_insensitively(tmp_path):
    _write(tmp_path / "SHOUTY.JPG", 100_000)
    _write(tmp_path / "MiXeD.JpEg", 100_000)

    DeleteFiles(str(tmp_path)).delete_files_less_than_desired_size()

    assert not (tmp_path / "SHOUTY.JPG").exists()
    assert not (tmp_path / "MiXeD.JpEg").exists()


def test_delete_leaves_unlisted_extensions_alone(tmp_path):
    _write(tmp_path / "voice_memo.m4a", 40_000)
    _write(tmp_path / "sticker.webp", 20_000)

    DeleteFiles(str(tmp_path)).delete_files_less_than_desired_size()

    assert (tmp_path / "voice_memo.m4a").exists()
    assert (tmp_path / "sticker.webp").exists()


def test_delete_recurses_into_a_sorted_tree(tmp_path):
    day = tmp_path / "Images" / "2024" / "June" / "15-06-24"
    _write(day / "whatsapp.jpg", 100_000)
    _write(day / "IMG_1.heic", 100_000)

    DeleteFiles(str(tmp_path)).delete_files_less_than_desired_size()

    assert not (day / "whatsapp.jpg").exists()
    assert (day / "IMG_1.heic").exists()


def test_delete_is_a_no_op_on_an_empty_folder(tmp_path):
    DeleteFiles(str(tmp_path)).delete_files_less_than_desired_size()

    assert list(tmp_path.iterdir()) == []


def test_locate_files_to_delete_honours_explicit_arguments(tmp_path):
    _write(tmp_path / "small.jpg", 100)
    _write(tmp_path / "small.png", 100)

    located = DeleteFiles(str(tmp_path)).locate_files_to_delete(1_000, [".jpg"])

    assert [os.path.basename(f) for f in located] == ["small.jpg"]
