""" Command module for the create commad

A convienice wrapper for conan create calls, adopted to our profile conventions
"""

import argparse
import sys
from . import base
from . import helpers
from typing import List
from sprun import spr

on_error_choices = ['ask', 'exit', 'continue']
on_error_options = [spr.Proceed.ASK, spr.Proceed.STOP ,spr.Proceed.CONTINUE]
on_error = dict(zip(on_error_choices, on_error_options))

class Command(base.Command):
    """ Create command implementation of the base.Command ''protocol''"""

    def name():
        """ The name implementation of the base.Command ''protocol''"""
        return helpers.mod_name(__file__)


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
        sub_cmd.add_argument(
            '--print-only',
            action='store_true',
            help="Do not run any commands, only print them out."
        )
        sub_cmd.add_argument('--onerror', choices=on_error_choices,
                    type=str, action='store', default='exit',
                help="Continuation strategy if a conan create command fails",
                required=False
        )
        sub_cmd.set_defaults(func=Command.run)

    def run(parsed_args: argparse.Namespace, other_args: List[str]):
        """ The run implementation of the base.Command ''protocol''"""
        packages = helpers.parse_spec(parsed_args.spec_pkg)
        profile_args_list = [[]] # at least one run,
        if parsed_args.spec_profile:
            profile_args_list.clear()  # we will get our runs
            profile_list = helpers.parse_spec(parsed_args.spec_profile)
            for profile in profile_list:
                profile_args_list += helpers.profile_args_for(profile)
        commands: spr.CommandList = []
        for package in packages:
            con_file = helpers.get_conan_file(package)
            if not con_file:
                print("Error: Package not found:", package, file=sys.stderr)
                return False
            pkg_args = [con_file, package]
            for profile_args in profile_args_list:
                cmd = ["conan", "create", "--test-folder", "None"]
                cmd += profile_args
                if other_args:
                    cmd += other_args
                cmd += pkg_args
                commands.append(cmd)
        if parsed_args.print_only:
            for command in commands:
                spr.report_command("", command)
            return True
        err_strategy = on_error.get(parsed_args.onerror)
        print(err_strategy)
        result: spr.Result = spr.run(commands, err_strategy)
        for command in result.commands_ok:
            spr.report_command("OK:", command)
        for command in result.commands_error:
            spr.report_command("Error:", command, sys.stderr)
        return result.success()

