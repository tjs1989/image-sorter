#File sorter for cloud uploading

This has been created to help sort Image, Audio and Video files in a directory into date order.

You can then view each set of files in turn and name them ready for your cloud upload.

I have used this to assist me in uploading images to Amazon's Cloud Drive.

##Usage
Specify the folder which you would like to sort as an argument when you call the main script
e.g ``python main.py --media=/users/bob/media`` would sort the media folder for the user Bob. If no full path is specified then the script will error


##Final Structure
The final structure will be along the lines of
``-File Type
    -Year
      -Month
       -Date``

Additional file extensions can be added in the values in `file_format_config.py`