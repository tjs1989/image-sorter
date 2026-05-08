from unittest.mock import MagicMock, patch

import pytest

from pull.pull_from_android import PullFromAndroid


@pytest.fixture
def puller(tmp_path):
    return PullFromAndroid(str(tmp_path))


def _devices_stdout(*lines):
    body = "\n".join(lines)
    return f"List of devices attached\n{body}\n"


@patch("pull.pull_from_android.shutil.which", return_value="/usr/local/bin/adb")
@patch("pull.pull_from_android.subprocess.run")
def test_verify_adb_available_happy_path(mock_run, mock_which, puller):
    mock_run.return_value = MagicMock(
        stdout=_devices_stdout("ABCD1234\tdevice"), stderr="", returncode=0
    )
    puller.verify_adb_available()


@patch("pull.pull_from_android.shutil.which", return_value=None)
def test_verify_adb_available_missing_adb(mock_which, puller):
    with pytest.raises(RuntimeError, match="adb not found"):
        puller.verify_adb_available()


@patch("pull.pull_from_android.shutil.which", return_value="/usr/local/bin/adb")
@patch("pull.pull_from_android.subprocess.run")
def test_verify_adb_available_no_device(mock_run, mock_which, puller):
    mock_run.return_value = MagicMock(
        stdout="List of devices attached\n\n", stderr="", returncode=0
    )
    with pytest.raises(RuntimeError, match="No authorized"):
        puller.verify_adb_available()


@patch("pull.pull_from_android.shutil.which", return_value="/usr/local/bin/adb")
@patch("pull.pull_from_android.subprocess.run")
def test_verify_adb_available_unauthorized(mock_run, mock_which, puller):
    mock_run.return_value = MagicMock(
        stdout=_devices_stdout("ABCD1234\tunauthorized"), stderr="", returncode=0
    )
    with pytest.raises(RuntimeError, match="unauthorized"):
        puller.verify_adb_available()


@patch("pull.pull_from_android.shutil.which", return_value="/usr/local/bin/adb")
@patch("pull.pull_from_android.subprocess.run")
def test_verify_adb_available_multiple_devices(mock_run, mock_which, puller):
    mock_run.return_value = MagicMock(
        stdout=_devices_stdout("AAA\tdevice", "BBB\tdevice"), stderr="", returncode=0
    )
    with pytest.raises(RuntimeError, match="Multiple devices"):
        puller.verify_adb_available()


@patch("pull.pull_from_android.subprocess.run")
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


@patch("pull.pull_from_android.subprocess.run")
def test_pull_folders_continues_when_one_path_fails(mock_run, puller):
    expected_count = len(puller.system_config["android_source_paths"])
    mock_run.side_effect = [
        MagicMock(stdout="", stderr="remote object does not exist", returncode=1)
    ] + [
        MagicMock(stdout="", stderr="", returncode=0)
        for _ in range(expected_count - 1)
    ]
    puller.pull_folders()
    assert mock_run.call_count == expected_count


@patch.object(PullFromAndroid, "pull_folders")
@patch.object(PullFromAndroid, "verify_adb_available")
def test_pull_orchestrates_verify_then_pull(mock_verify, mock_pull, puller):
    puller.pull()
    mock_verify.assert_called_once()
    mock_pull.assert_called_once()
    # destination dir created as a side effect
    import os
    assert os.path.isdir(puller.destination_path)
