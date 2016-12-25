import argparse
import sys
from argparse import RawTextHelpFormatter


def exit_with_failure(msg='failure', status=1):
    sys.stderr.write(msg+'\n')
    sys.stderr.flush()
    sys.exit(status)


class ArgParser(argparse.ArgumentParser):
    """
    Wrap default ArgParser implementation adding the ability to supress
    a positional argument from the example cammand output by the
    print_help method.
    """

    def __init__(self, *args, **kwargs):
        if 'formatter_class' not in kwargs:
            kwargs['formatter_class'] = RawTextHelpFormatter
        super(ArgParser, self).__init__(*args, **kwargs)
        self._errors = []

    def error(self, err):
        self._errors.append(err)

    def supress_positional(self, dest):
        for i in self._positionals._group_actions:
            if i.dest == dest:
                i.help = argparse.SUPPRESS


argparser = ArgParser(
    description='xvm - Light virtual machines for OSX',
    add_help=False,
)
