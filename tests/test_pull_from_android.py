from unittest.mock import MagicMock, patch

import pytest

from pull.pull_from_android import PullFromAndroid


@pytest.fixture
def puller(tmp_path):
    return PullFromAndroid(str(tmp_path))


def _devices_stdout(*lines):
    body = "\n".join(lines)
    return f"List of devices attached\n{body}\n"


@pytest.mark.parametrize(
    "which_returns,devices_stdout,expected_error",
    [
        pytest.param("/usr/local/bin/adb", _devices_stdout("ABCD\tdevice"), None, id="happy"),
        pytest.param(None, "", "adb not found", id="missing-adb"),
        pytest.param("/usr/local/bin/adb", "List of devices attached\n\n", "No authorized", id="no-device"),
        pytest.param("/usr/local/bin/adb", _devices_stdout("ABCD\tunauthorized"), "unauthorized", id="unauthorized"),
        pytest.param("/usr/local/bin/adb", _devices_stdout("AAA\tdevice", "BBB\tdevice"), "Multiple devices", id="multi-device"),
    ],
)
def test_verify_adb_available(which_returns, devices_stdout, expected_error, puller):
    with patch("pull.pull_from_android.shutil.which", return_value=which_returns), \
         patch("pull.pull_from_android.subprocess.run",
               return_value=MagicMock(stdout=devices_stdout, stderr="", returncode=0)):
        if expected_error is None:
            puller.verify_adb_available()
        else:
            with pytest.raises(RuntimeError, match=expected_error):
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
        MagicMock(stdout="", stderr="", returncode=0) for _ in range(expected_count - 1)
    ]
    puller.pull_folders()
    assert mock_run.call_count == expected_count


@patch.object(PullFromAndroid, "pull_folders")
@patch.object(PullFromAndroid, "verify_adb_available")
def test_pull_orchestrates_verify_then_pull(mock_verify, mock_pull, puller):
    import os
    puller.pull()
    mock_verify.assert_called_once()
    mock_pull.assert_called_once()
    assert os.path.isdir(puller.destination_path)
