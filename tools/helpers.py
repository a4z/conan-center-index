""" Some helpers that deserve test functions
"""
import os
from typing import Optional


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

# only for debug ...
# if __name__ == '__main__':
#     is_reference_name("/1.2.3@")
