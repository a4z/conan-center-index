""" Command module for the create commad

A convienice wrapper for conan create calls, adopted to our profile conventions
"""

import argparse
from . import base
from . import helpers
from typing import List


class Command(base.Command):
    """ Create command implementation of the base.Command ''protocol''"""

    def setup(sub_cmd: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """ The setup implementation of the base.Command ''protocol''"""
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
        """ The run implementation of the base.Command ''protocol''"""
        packages = helpers.parse_spec(parsed_args.spec_pkg)
        profiles = []
        if parsed_args.spec_profile:
            profile_list = helpers.parse_spec(parsed_args.spec_profile)
            for profile in profile_list:
                profiles += helpers.get_profile_args_for(profile)
        if not profiles:
            profiles.append([]) # at least one run
        # TODO, package fore each profile or all packages per profile...
        for package in packages:
            for profile in profiles:
                print(package, profile)
