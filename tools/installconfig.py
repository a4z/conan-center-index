#!/usr/bin/env python3
"""Utility to install the config subfolder from ../configs/[subfolder]

Note that those profiles are only needed for development of packages.
For using packages, use lockfiles.
"""
import os
import sys
import traceback
import argparse
import textwrap
import platform
import pathlib
from sprun import spr


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
                             "settings.os.arch=armv8", name])
            commands.append(["conan", "profile", "update",
                             "settings.os.arch_build=armv8", name])
    # Windows no known actions at the moment
    return commands


def install_config(name: str):
    """ Builds, and runs all the commands,
        This is the actual entrypoint, after doing input and other validations
    """
    path = pathlib.Path(__file__).parent.parent / "configs" / name
    if not path.exists():
        print(f"Config directory not found: {name}")
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
    spr.run(commands, on_error=spr.Proceed.STOP)
    return True


def list_configs():
    """ Returns a list of configs (directory in repositories configs folder)
    """
    # yes, depends heavily on the current path
    # (maybe) add an environment variable where our cci is
    path = pathlib.Path(__file__).parent.parent / "configs"
    return next(os.walk(path))[1]


def main(argv) -> bool:
    """ The entry point which takes all the command line arguments
    """
    def tool_help() -> str:
        """Command line help text to get line breaks as written here"""
        return """\
            Get the conan package developer setup for the give schema
            Recommended to us in a custom CONAN_USER_HOME directory.
        """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(tool_help()),
        epilog="",
    )
    parser.add_argument(
        "--list",
        help="List available configurations",
        action="store_true")  # feature creep
    parser.add_argument(
        "-c",
        "--config",
        help="Specify wanted configurations",
        type=str)  # use nsdk-devel as default?
    args = parser.parse_args(sys.argv[1:])
    if args.list:
        for dir_name in list_configs():
            print(dir_name)
        return False
    if not args.config:
        print("-c/--config required", file=sys.stderr)
    if not args.config in list_configs():
        print(f"Config {args.config} not found", file=sys.stderr)
        return False
    return install_config(str(args.config))


if __name__ == "__main__":
    try:
        if not main(sys.argv[1:]):
            sys.exit(1)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
