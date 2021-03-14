""" Some helpers that deserve test functions
"""
import os
import sys
from typing import Optional
from typing import List
import yaml


def is_reference_name(reference: str) -> bool:
    """ Checks if a given reference is a valid reference name
        This might not implement 100% of all conan naming rules, but only those we use

        Avalid reference is either name/version@ or name/version@user/channel
    """
    name_channel = reference.split("@")
    if len(name_channel) != 2:
        return False
    name_version = name_channel[0].split("/")
    if len(name_version) != 2:
        return False
    if not all(part for part in name_version):
        return False
    if name_channel[1]:
        user_channel = name_channel[1].split("/")
        if len(user_channel) != 2:
            return False
        if not all(part for part in user_channel):
            return False
    return True


def reference_name(reference: str) -> Optional[str]:
    """ Get the name of a conan reference
        Returns the name part of the reference, or None if the input reference
        does not follow a recognized name pattern
    """
    if not is_reference_name(reference):
        return None
    end = reference.find("@")
    slash = reference.find("/", 0, end)
    return reference[0:slash]


def reference_version(reference: str) -> Optional[str]:
    """ Get the versions of a conan reference
        Returns the name part of the reference, or None if the input reference
        does not follow a recognized name pattern
    """
    if not is_reference_name(reference):
        return None
    end = reference.find("@")
    start = reference.find("/", 0, end) + len("/")
    return reference[start:end]


def guess_recipe_dir(reference: str,
                     hint: Optional[str] = None) -> Optional[str]:
    """ Does best effort to guess a recipe directory for a reference
        Fits our current workflow, might be total useless for others

        This does only check for an existing directory of the reference name.
        If this directory contains a valid recipe is an other question.

        The search order is, in that order
            hint, if provided
            os.getenv('CONAN_RECIPE_DIRS', "").split(":")
            ../recipes to this module file

        A recipe dir must match the name of a reference
    """
    assert is_reference_name(reference)
    name = reference_name(reference)
    if hint:
        check_path = os.path.join(hint, name)
        if os.path.isdir(check_path):
            return check_path
    usr_dirs = os.getenv('CONAN_RECIPE_DIRS', "").split(":")
    while "" in usr_dirs:
        usr_dirs.remove("")
    for item in usr_dirs:
        check_path = os.path.join(item, name)
        if os.path.isdir(check_path):
            return check_path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.dirname(dir_path)
    check_path = os.path.join(dir_path, "recipes", name)
    if os.path.isdir(check_path):
        return check_path
    return None


# consider optional parameter, taking a folder name (path)
# and skip the guess. Maybe a named parameter ...
def get_conan_file(reference: str) -> Optional[str]:
    """ Guess the reference dir and return path to the conan file in it.
    Handles cases:,
        a directory that contains the config.yml , as cci does
        a directory that contains the conanfile.py
    """
    # the easy part, in the dir is a conanfile.py, take that
    recipe_dir = guess_recipe_dir(reference)
    if not recipe_dir:
        return print("Can'f guess folder for", reference)
    conan_file = os.path.join(recipe_dir, "conanfile.py")
    if os.path.isfile(conan_file):
        return conan_file
    # maybe a cci folder, so check
    config_yml = os.path.join(recipe_dir, "config.yml")
    version = reference_version(reference)
    if os.path.isfile(config_yml):
        with open(config_yml) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            try:
                subfolder = data["versions"][version]["folder"]
            except KeyError:
                valid_versions = list(data["versions"].keys())
                print("Error: Version", version, "not found!", file=sys.stderr)
                print(
                    "Error: Valid versions:",
                    ", ".join(valid_versions),
                    file=sys.stderr)
                print("", file=sys.stderr)
                return None
    else:
        subfolder = version
        # this covers something that in today's cci layout should no exist
        # but that was there, or in bincrafter, so leaf that for now

    conan_file = os.path.join(recipe_dir, subfolder, "conanfile.py")
    if os.path.isfile(conan_file):
        return conan_file
    return print("Error: Conan file not found:", conan_file, file=sys.stderr)


def parse_spec(arg: str) -> List[str]:
    """ If arg is a file, returns the file contend as list
        Note the a file must have 1 package name per line

    If arg is not a file, it is interpreted as a comma seperated string,
    and returns that as a list, splitted at every occuring ","

    The returned package names are trimmed and empty values are remmoved.
    Entries starting with # will also be removed
    """
    if os.path.isfile(arg):
        with open(arg, 'r') as file:
            packages = file.readlines()
    else:
        packages = arg.split(",")

    filtered = filter(lambda item: item != "" and not item.startswith("#"),
                      map(str.strip, packages))
    return list(filtered)


# only for debug ...
# if __name__ == '__main__':
#     is_reference_name("/1.2.3@")
