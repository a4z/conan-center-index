#!/usr/bin/env python3
""" Utility to run our package creation tasks
"""

import sys
import traceback
import argparse
import textwrap
from typing import List

from . import helpers as helpers


def create(parsed_args: argparse.Namespace, other_args: List[str]):
    package_list = helpers.parse_spec(parsed_args.spec_pkg)
    if parsed_args.spec_profile:
        profile_args = helpers.parse_
    for package in package_list:
        print(package)


def upload(parsed_args: argparse.Namespace, other_args: List[str]):
    ...


def main(argv: List[str]) -> bool:
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
    # --- create
    create_cmd = subparser.add_parser(
        "create", help="Create given packages to given profiles")
    create_cmd.add_argument(
        '--spec-pkg',
        type=str, action='store', required=True,
        help='Package spec, file or list of package')
    create_cmd.add_argument(
        '--spec-profile',
        type=str, action='store', required=False,
        help='Profile spec, list of profiles')
    create_cmd.set_defaults(func=create)
    # --- upload
    upload_cmd = subparser.add_parser("upload", help="Upload given packages.\n"
                                      "Best effort to create a query from given profiles in case profiles are used")
    upload_cmd.add_argument(
        '--spec-pkg',
        type=str, action='store', required=True,
        help='Package spec, file or list of package')
    upload_cmd.add_argument(
        '--spec:profile',
        type=str, action='store', required=False,
        help='Profile spec, list of profiles')
    upload_cmd.set_defaults(func=upload)
    # --- lint
    upload_cmd = subparser.add_parser("lint", help="Runs lint tests for given package")
    upload_cmd.add_argument(
        '--spec-pkg',
        type=str, action='store', required=True,
        help='Package spec, file or list of package')
    upload_cmd.add_argument(
        '--spec-profile',
        type=str, action='store', required=False,
        help='Profile spec, list of profiles')

    parser.add_argument('--print-only', action='store_true', default=False,
        help="Do not run any commands, only print them out. "
    )

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
