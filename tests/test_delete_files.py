import os

import pytest

from delete.delete_files import DeleteFiles


def _write(path, size_in_bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"0" * size_in_bytes)


@pytest.mark.parametrize(
    "filename,size_in_bytes,survives",
    [
        pytest.param("whatsapp.jpg", 200_000, False, id="small-jpg"),
        pytest.param("sticker.gif", 50_000, False, id="small-gif"),
        pytest.param("forwarded.mp4", 400_000, True, id="small-mp4-left-to-the-iphone-discard"),
        pytest.param("SHOUTY.JPG", 100_000, False, id="uppercase-extension"),
        pytest.param("MiXeD.JpEg", 100_000, False, id="mixed-case-extension"),
        pytest.param("real_photo.jpg", 2_000_000, True, id="listed-but-over-threshold"),
        pytest.param("IMG_1.heic", 800_000, True, id="small-heic-camera-original"),
        pytest.param("IMG_2.mov", 300_000, True, id="small-mov-camera-original"),
        pytest.param("voice_memo.m4a", 40_000, True, id="small-unlisted-audio"),
        pytest.param("sticker.webp", 20_000, True, id="small-unlisted-image"),
    ],
)
def test_delete_applies_the_size_and_extension_gates_together(tmp_path, filename, size_in_bytes, survives):
    _write(tmp_path / filename, size_in_bytes)

    DeleteFiles(str(tmp_path)).delete_files_less_than_desired_size()

    assert (tmp_path / filename).exists() == survives


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
