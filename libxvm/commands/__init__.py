from .common import argparser
from .create import create
from .start import start

def list_commands(argparser=argparser, show_help=False):
    if show_help:
        argparser.print_help()
        sys.exit(0)
    print("Available commands are:")
    for i in COMMANDS:
        print("  " + i)

COMMANDS = {
    'list': list_commands,
    'create': create,
    'start': start,
}
