# File sorter for cloud uploading

This has been created to help sort Image, Audio and Video files in a directory into date order.

You can then view each set of files in turn and name them ready for your cloud upload.

I have used this to assist me in uploading images to Amazon's Cloud Drive.

## Usage
Specify the folder which you would like to sort as an argument when you call the main script
e.g ``python main.py sort -f=/users/bob/media`` would sort the media folder for the user Bob. If no full path is specified then the script will error


## Final Structure
The final structure will be along the lines of
``-File Type
    -Year
      -Month
       -Date``

## Deleting files
Files less than 1MB can also be deleted in a completed folder structure. To do this you can call the delete function.
e.g ``python main.py delete -f=/users/bob/media`` would delete any files less than 1MB in `/users/bob/media`, and any sub folders.
If any folders become empty as a result of the deletion, they too are removed.

## Pulling from an Android device
You can pull media off a USB-connected Android phone (replacing the old Android File Transfer / Android Device Manager workflow) using `adb`.

Prerequisites:
- Install adb: ``brew install --cask android-platform-tools``
- Enable Developer Options and USB debugging on the phone, then accept the USB debugging prompt when you plug it in.

Then:
``python main.py pullmedia -f=/users/bob/media`` will copy `/sdcard/DCIM`, `/sdcard/Pictures`, `/sdcard/Movies` and `/sdcard/Music` into `/users/bob/media`, preserving the phone's subfolder structure. After it finishes, run ``python main.py sort -f=/users/bob/media`` and the sort will recurse into those folders.

The list of source paths on the device is configurable via ``android_source_paths`` in ``config/system_config.yaml``.