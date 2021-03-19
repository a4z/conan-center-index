import argparse
from . import base
from . import helpers
from typing import List
import os


class Command(base.Command):
    """Remove command implementation of the base.Command ''protocol''"""

    @staticmethod
    def name():
        """ The name implementation of the base.Command ''protocol''"""
        return helpers.mod_name(__file__)

    @staticmethod
    def setup(sub_cmd: argparse.ArgumentParser) -> None:
        """ The setup implementation of the base.Command ''protocol''"""
        sub_cmd.set_defaults(func=Command.run)

    @staticmethod
    def run(parsed_args: argparse.Namespace, other_args: List[str]):
        """ The run implementation of the base.Command ''protocol''"""
        print("Not implemented yet:", Command.name())
        return False
