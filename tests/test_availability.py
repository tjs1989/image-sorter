from unittest.mock import MagicMock, patch

import pytest

from adb.availability import Availability


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
def test_verify(which_returns, devices_stdout, expected_error):
    with patch("adb.availability.shutil.which", return_value=which_returns), \
         patch("adb.availability.subprocess.run",
               return_value=MagicMock(stdout=devices_stdout, stderr="", returncode=0)):
        if expected_error is None:
            Availability().verify()
        else:
            with pytest.raises(RuntimeError, match=expected_error):
                Availability().verify()
