
import argparse
#from .helpers import *
from . import helpers
from typing import List

def setup_run_args(sub_cmd):
    sub_cmd.add_argument(
        '--spec-pkg',
        type=str, action='store', required=True,
        help='Package spec, file or list of package')
    sub_cmd.add_argument(
        '--spec-profile',
        type=str, action='store', required=False,
        help='Profile spec, list of profiles')

def run(parsed_args: argparse.Namespace, other_args: List[str]):
    package_list = helpers.parse_spec(parsed_args.spec_pkg)
    if parsed_args.spec_profile:
        profile_args = helpers.parse_spec("")
    for package in package_list:
        print(package)
