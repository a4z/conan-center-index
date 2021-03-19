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

    subparser = parser.add_subparsers(
        help="The following subcommands are supported:")

    def add_command(command, **kwargs):
        command.setup(subparser.add_parser(
            command.name(), **kwargs
        ))
    add_command(
        create.Command,
        help="Create given packages to given profiles")
    add_command(
        config.Command,
        help="Install profiles and config")
    add_command(
        delete.Command,
        help="Delete packages (for give profiles (future/feature))")
    add_command(
        lock.Command,
        help="Creates lockfiles for a given conan file")
    add_command(
        lint.Command,
        help="Run lint tests ...")
    add_command(
        upload.Command,
        help="Upload packages (for give profiles (future/feature))")

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
