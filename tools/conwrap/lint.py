""" Implementation of the lint Command
"""
import argparse
import os
import sys
from typing import List
from sprun import spr
from . import helpers
from . import base


def checks_dir_path() -> str:
    """ Get a path to the config directory
    """
    return os.path.join(helpers.my_cci_root(), "pkgchecks")


def list_checks() -> List[str]:
    """ Returns a list of configs (directory in repositories configs folder)
    """
    path = checks_dir_path()
    return next(os.walk(path))[1]


def errmsg(msg: str) -> None:
    """Write msg to stderr, with Error as prefix"""
    print("Error:", msg, file=sys.stderr)


class Command(base.Command):
    """Lint command implementation of the base.Command ''protocol''"""

    @staticmethod
    def name():
        """ The name implementation of the base.Command ''protocol''"""
        return helpers.mod_name(__file__)

    @staticmethod
    def setup(sub_cmd: argparse.ArgumentParser) -> None:
        """ The setup implementation of the base.Command ''protocol''"""
        sub_cmd.add_argument(
            "--list",
            help="List available check",
            action="store_true")
        sub_cmd.add_argument(
            "-c",
            "--check",
            help="Specify wanted check",
            type=str)
        sub_cmd.add_argument(
            "-r",
            "--reference",
            help="Package to test",
            type=str)
        sub_cmd.add_argument(
            '--print-only',
            action='store_true',
            help="Do not run any commands, only print them out."
        )
        sub_cmd.set_defaults(func=Command.run)

    @staticmethod
    def run(parsed_args: argparse.Namespace, other_args: List[str]):
        """ The run implementation of the base.Command ''protocol''"""
        if parsed_args.list:
            for dir_name in list_checks():
                print(dir_name)
            return True
        if not parsed_args.check:
            errmsg("-c/--check required")
            return False
        if not parsed_args.check in list_checks():
            errmsg("Check {parsed_args.check} not found")
            return False
        if not parsed_args.reference:
            errmsg("-r/--reference required")
        if not helpers.is_reference_name(parsed_args.reference):
            errmsg(f"{parsed_args.reference} does not look like a reference")
            return False
        test_folder = os.path.join(helpers.my_cci_root(),
                                   "pkgchecks", parsed_args.check)
        command = ["conan", "test", test_folder, parsed_args.reference]
        if parsed_args.print_only:
            print(" ".join(command))
            return True
        result = spr.run([command], spr.Proceed.CONTINUE)
        return result.success()
