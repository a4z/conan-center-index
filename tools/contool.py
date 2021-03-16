#!/usr/bin/env python3
""" Utility to run our package creation tasks
"""

import sys
import traceback
import sys
import traceback
import argparse
import textwrap
from conwrap import create


def main(argv):
    """ The entry point which takes all the command line arguments
    """
    def tool_help() -> str:
        """Command line help text to get line breaks as written here"""
        return """\
            A wrapper for some conan package developer commands.
            Recommended: Work with a custom CONAN_USER_HOME directory.
        """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(tool_help()),
        epilog="",
    )
    subparser = parser.add_subparsers(
        help="Following subcommands are supported:")

    create_cmd = subparser.add_parser(
        "create", help="Create given packages to given profiles")
    create.setup_run_args(create_cmd)
    create_cmd.set_defaults(func=create.run)

    parsed_args, other_args = parser.parse_known_args(argv)
    parsed_args.func(parsed_args, other_args)

if __name__ == "__main__":
    try:
        if not main(sys.argv[1:]):
            sys.exit(1)
    # pylint: disable=W0703
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)

