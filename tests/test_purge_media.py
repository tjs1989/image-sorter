from unittest.mock import MagicMock, patch

import pytest

from adb.purge_media import PurgeMedia


@pytest.fixture
def purger():
    return PurgeMedia()


@patch("adb.purge_media.subprocess.run")
def test_purge_folders_calls_adb_for_each_configured_path(mock_run, purger):
    mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
    purger.purge_folders()

    expected_remote_paths = purger.system_config["android_source_paths"]
    assert mock_run.call_count == len(expected_remote_paths)

    for call, expected_path in zip(mock_run.call_args_list, expected_remote_paths):
        cmd = call.args[0]
        assert cmd[0:3] == ["adb", "shell", "find"]
        assert cmd[3] == expected_path
        assert cmd[-3:] == ["-mindepth", "1", "-delete"]


@patch("adb.purge_media.subprocess.run")
def test_purge_folders_continues_when_one_path_fails(mock_run, purger):
    expected_count = len(purger.system_config["android_source_paths"])
    mock_run.side_effect = [
        MagicMock(stdout="", stderr="not found", returncode=1)
    ] + [
        MagicMock(stdout="", stderr="", returncode=0) for _ in range(expected_count - 1)
    ]
    purger.purge_folders()
    assert mock_run.call_count == expected_count


@patch("adb.purge_media.subprocess.run")
def test_trigger_media_rescan_invokes_content_scan_volume(mock_run, purger):
    mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
    purger.trigger_media_rescan()

    cmd = mock_run.call_args.args[0]
    assert cmd[0:2] == ["adb", "shell"]
    assert "content" in cmd and "call" in cmd
    assert "scan_volume" in cmd
    assert "name:s:external_primary" in cmd


@pytest.mark.parametrize(
    "user_input,should_purge",
    [("confirm", True), ("no", False), ("Confirm", False)],
    ids=["confirmed", "rejected", "wrong_case"],
)
@patch.object(PurgeMedia, "trigger_media_rescan")
@patch.object(PurgeMedia, "purge_folders")
def test_purge_runs_only_when_token_typed_exactly(
    mock_purge, mock_rescan, purger, user_input, should_purge
):
    purger.availability = MagicMock()
    with patch("builtins.input", return_value=user_input):
        purger.purge()

    purger.availability.verify.assert_called_once()
    assert mock_purge.called is should_purge
    assert mock_rescan.called is should_purge
