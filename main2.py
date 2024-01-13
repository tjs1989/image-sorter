"""
Example taken from https://mike.depalatis.net/blog/simplifying-argparse.html
"""

import logging
from argparse import ArgumentParser
from config.setup import get_system_config

version = 2.0

cli = ArgumentParser(description="Image Sorter")
cli.add_argument("-d", "--debug", help="enable debug logger", action='store_true')
cli.add_argument("-v", "--version", action="version", version=f"Image Sorter {version}")
subparsers = cli.add_subparsers(dest="subcommand")


def initialise_logger(level):
    system_config_yaml = get_system_config()

    logging.basicConfig(level=level,
                        format=system_config_yaml['logging_formats']['string_format'],
                        datefmt=system_config_yaml['logging_formats']['date_format'],
                        handlers=[
                            logging.FileHandler("debug.log"),
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


@subcommand([argument("-f", "--folder", help="The full path to the folder where your media is located")])
def sort(args):
    print(args.folder)


@subcommand([argument("-f", "--folder", help="The full path where you would like to delete images less than 1MB in")])
def delete(args):
    print(args.folder)



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
