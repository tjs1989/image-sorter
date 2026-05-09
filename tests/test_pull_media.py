import os
from unittest.mock import MagicMock, patch

import pytest

from adb.pull_media import PullMedia


@pytest.fixture
def puller(tmp_path):
    return PullMedia(str(tmp_path))


@patch("adb.pull_media.subprocess.run")
def test_pull_folders_calls_adb_for_each_configured_path(mock_run, puller):
    mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
    puller.pull_folders()

    expected_remote_paths = puller.system_config["android_source_paths"]
    assert mock_run.call_count == len(expected_remote_paths)

    actual_remote_paths = [call.args[0][2] for call in mock_run.call_args_list]
    assert actual_remote_paths == expected_remote_paths

    for call in mock_run.call_args_list:
        cmd = call.args[0]
        assert cmd[0] == "adb"
        assert cmd[1] == "pull"
        assert cmd[3] == puller.destination_path


@patch("adb.pull_media.subprocess.run")
def test_pull_folders_continues_when_one_path_fails(mock_run, puller):
    expected_count = len(puller.system_config["android_source_paths"])
    mock_run.side_effect = [
        MagicMock(stdout="", stderr="remote object does not exist", returncode=1)
    ] + [
        MagicMock(stdout="", stderr="", returncode=0) for _ in range(expected_count - 1)
    ]
    puller.pull_folders()
    assert mock_run.call_count == expected_count


@patch.object(PullMedia, "pull_folders")
def test_pull_orchestrates_verify_then_pull(mock_pull, puller):
    puller.availability = MagicMock()

    puller.pull()

    puller.availability.verify.assert_called_once()
    mock_pull.assert_called_once()
    assert os.path.isdir(puller.destination_path)
