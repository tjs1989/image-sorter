from config.setup import get_system_config
from main import cli


def test_sort_defaults_to_android():
    args = cli.parse_args(["sort", "-f", "/some/path"])

    assert args.phone == "android"


def test_sort_accepts_every_phone_type_in_the_config():
    for phone_type in get_system_config()['discard_file_extensions']:
        args = cli.parse_args(["sort", "-f", "/some/path", "-p", phone_type])

        assert args.phone == phone_type
