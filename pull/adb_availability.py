import shutil
import subprocess


class AdbAvailability:
    def verify(self):
        if shutil.which("adb") is None:
            raise RuntimeError(
                "adb not found on PATH. Install with: "
                "brew install --cask android-platform-tools"
            )

        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True, check=True
        )
        device_lines = result.stdout.splitlines()[1:]
        authorized = [line for line in device_lines if "\tdevice" in line]
        unauthorized = [line for line in device_lines if "\tunauthorized" in line]

        if unauthorized:
            raise RuntimeError(
                "Device connected but unauthorized. "
                "Accept the USB debugging prompt on the phone and re-run."
            )
        if not authorized:
            raise RuntimeError(
                "No authorized Android device detected. "
                "Connect via USB with USB debugging enabled."
            )
        if len(authorized) > 1:
            raise RuntimeError("Multiple devices detected. Disconnect all but one.")
