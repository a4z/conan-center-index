import argparse
from . import base
from . import helpers
from typing import List


class Command(base.Command):

    def setup(sub_cmd: argparse.ArgumentParser) -> None:
        sub_cmd.set_defaults(func=Command.run)

    def run(parsed_args: argparse.Namespace, other_args: List[str]):
        print("Run lock")
