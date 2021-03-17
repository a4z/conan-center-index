
import argparse
from . import base
from . import helpers
from typing import List
class Command(base.Command):

    def setup(sub_cmd: argparse.ArgumentParser) -> argparse.ArgumentParser:
        sub_cmd.add_argument(
            '--spec-pkg',
            type=str, action='store', required=True,
            help='Package spec, file or list of package')
        sub_cmd.add_argument(
            '--spec-profile',
            type=str, action='store', required=False,
            help='Profile spec, list of profiles')
        sub_cmd.set_defaults(func=Command.run)

    def run(parsed_args: argparse.Namespace, other_args: List[str]):
        package_list = helpers.parse_spec(parsed_args.spec_pkg)
        if parsed_args.spec_profile:
            profile_args = helpers.parse_spec("")
        for package in package_list:
            print(package)
