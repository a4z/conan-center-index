#!/usr/bin/env python3
"""Utility to install the config subfolder from ../../configs/[subfolder]
Yes, it dependes very much on the path
Note that those profiles are only needed for development of packages.
For using packages, use lockfiles.
"""
import os
import sys
import platform
import pathlib
import argparse
from typing import List
from sprun import spr

from . import helpers
from . import base
#from . import helpers


def config_dir_path() -> pathlib.Path:
    """ Get a path to the config directory

        Depends heavily on the current __file__ path
        TODO (maybe) add an environment variable where our cci is
    """
    return pathlib.Path(helpers.my_cci_root()) / "configs"


def create_default_profile(name: str) -> spr.Command:
    """Create command to auto detected profile with the given name"""
    return ["conan", "profile", "new", "--detect", "--force", name]


def fix_platform_profile(name: str) -> spr.CommandList:
    """Create commands for defaults we expect to a given profile"""
    commands: spr.CommandList = []
    cmd = ["conan", "profile", "update", "settings.compiler.cppstd=17", name]
    commands.append(cmd)
    if platform.system() == "Linux":
        cmd = [
            "conan",
            "profile",
            "update",
            "settings.compiler.libcxx=libstdc++11",
            name,
        ]
        commands.append(cmd)
    if platform.system() == "Darwin":
        commands.append(["conan", "profile", "update",
                         "settings.os.sdk=macosx", name])
        commands.append([
            "conan",
            "profile",
            "update",
            "settings.os.subsystem=None",
            name])
        if platform.processor() == "arm":
            commands.append(["conan", "profile", "update",
                             "settings.arch=armv8", name])
            commands.append(["conan", "profile", "update",
                             "settings.arch_build=armv8", name])
    # Windows no known actions at the moment
    return commands


def fix_ios_sim_profile(name):
    """Update ios profiles like needed"""
    arch = "x86_64"
    toolchain_target = "SIMMULATOR64"
    if platform.processor() == "arm":
        arch = "armv8"
        toolchain_target = "SIMMULATORARM64"
    commands: spr.CommandList = []
    commands.append(["conan", "profile", "update",
                     f"settings.arch={arch}", name])
    commands.append(["conan", "profile", "update",
                     f"options.ios-cmake:toolchain_target={toolchain_target}", name])
    return commands


def install_config(name: str) -> bool:
    """ Builds, and runs all the commands,
        This is the actual entrypoint, after doing input and other validations
    """
    path = config_dir_path() / name
    if not path.exists():
        print(f"Config directory not found: {name}", file=sys.stderr)
        return False
    cmd = [
        "conan",
        "config",
        "install",
        "--type", "dir",
        path.as_posix()
    ]
    commands: spr.CommandList = []
    commands.append(cmd)
    commands.append(create_default_profile("native"))
    commands += fix_platform_profile("native")
    if platform.system() == "Darwin":
        commands += fix_ios_sim_profile("ios-simulator")
    result = spr.run(commands, on_error=spr.Proceed.STOP)
    return result.success()


def list_configs() -> List[str]:
    """ Returns a list of configs (directory in repositories configs folder)
    """
    path = config_dir_path()
    return next(os.walk(path))[1]


class Command(base.Command):
    """ Config command implementation of the base.Command ''protocol''"""

    @staticmethod
    def name():
        """ The name implementation of the base.Command ''protocol''"""
        return helpers.mod_name(__file__)

    @staticmethod
    def setup(sub_cmd: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """ The setup implementation of the base.Command ''protocol''"""
        sub_cmd.add_argument(
            "--list",
            help="List available configurations",
            action="store_true")  # feature creep
        sub_cmd.add_argument(
            "-n",
            "--name",
            help="Specify wanted configurations",
            type=str)  # use nsdk-devel as default?
        sub_cmd.set_defaults(func=Command.run)

    @staticmethod
    def run(parsed_args: argparse.Namespace, other_args: List[str]):
        """ The run implementation of the base.Command ''protocol''"""
        if parsed_args.print_only:
            print("Print only")

        if parsed_args.list:
            for dir_name in list_configs():
                print(dir_name)
            return True

        if not parsed_args.name:
            print("-n/--name required", file=sys.stderr)
        if not parsed_args.name in list_configs():
            print(f"Config {parsed_args.name} not found", file=sys.stderr)
            return False
        return install_config(str(parsed_args.name))
