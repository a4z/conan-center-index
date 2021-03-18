#!/usr/bin/env python3
""" Utility to run our package creation tasks

    each subcommand is implemented in conwarp
    by implementing the conwarp.base.Command ''protocol''

"""
import sys
import traceback
import argparse
import textwrap
from conwrap import create
from conwrap import lock
from conwrap import lint
from conwrap import upload
from conwrap import delete
from conwrap import config


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

    # all commands have a print only
    parser.add_argument('--print-only', action='store_true',
                        help="Do not run any commands, only print them out."
                        "NOTE: If used, must be provided before a sub command."
                        )

    subparser = parser.add_subparsers(
        help="The following subcommands are supported:")

    create.Command.setup(subparser.add_parser(
        "create",
        help="Create given packages to given profiles"
    ))
    config.Command.setup(subparser.add_parser(
        "config",
        help="Install profiles and config"
    ))
    delete.Command.setup(subparser.add_parser(
        "delete",
        help="Delete packages (for give profiles (future/feature))"
    ))
    lock.Command.setup(subparser.add_parser(
        "lock",
        help="Creates lockfiles for a given conan file"
    ))
    lint.Command.setup(subparser.add_parser(
        "lint",
        help="Run lint tests with much more text and ed"
    ))
    upload.Command.setup(subparser.add_parser(
        "upload",
        help="Upload packages (for give profiles (future/feature))"
    ))

    parsed_args, other_args = parser.parse_known_args(argv)
    if not hasattr(parsed_args, "func"):
        print("Error: Command required, non provided", file=sys.stderr)
        return False
    return parsed_args.func(parsed_args, other_args)


if __name__ == "__main__":
    try:
        if not main(sys.argv[1:]):
            sys.exit(1)
    # pylint: disable=W0703
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
