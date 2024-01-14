"""
Example taken from https://mike.depalatis.net/blog/simplifying-argparse.html
"""

import logging
from argparse import ArgumentParser
from config.setup import get_system_config
from sort import sort_files
from delete import delete_files

version = 2.0

cli = ArgumentParser(description="Image Sorter")
cli.add_argument("-d", "--debug", help="enable debug logger", action='store_true')
cli.add_argument("-v", "--version", action="version", version=f"Image Sorter {version}")
subparsers = cli.add_subparsers(dest="subcommand")


def initialise_logger(level):
    system_config_yaml = get_system_config()

    log_file_name = system_config_yaml['log_file_name']
    file = open(log_file_name, "w+")
    file.truncate(0)
    file.close()

    logging.basicConfig(level=level,
                        format=system_config_yaml['logging_formats']['string_format'],
                        datefmt=system_config_yaml['logging_formats']['date_format'],
                        handlers=[
                            logging.FileHandler(log_file_name),
                            logging.StreamHandler()
                        ]
                        )


def argument(*name_or_flags, **kwargs):
    return list(name_or_flags), kwargs


def subcommand(args=None, parent=subparsers):
    if args is None:
        args = []

    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)

    return decorator


@subcommand([argument("-f", "--folder", help="The full path to the folder where your media is located", required=True)])
def sort(args):
    file_sort_class = sort_files.SortFiles(args.folder)
    file_sort_class.sort_files_into_folders()


@subcommand([argument("-f", "--folder", help="The full path where you would like to delete images less than 1MB in")])
def delete(args):
    file_deletion = delete_files.DeleteFiles("/Users/tony/Desktop/thing2")
    file_deletion.locate_and_delete_files()



if __name__ == "__main__":
    args = cli.parse_args()

    if args.debug:
        initialise_logger(level=logging.DEBUG)
    else:
        initialise_logger(level=logging.INFO)

    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(args)
