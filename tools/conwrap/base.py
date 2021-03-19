""" Provides the abstract Command ''protocol''
"""
from abc import ABC, abstractmethod
import argparse
from . import helpers
from typing import List


class Command(ABC):
    """ Abstract base, specifying the ''command protocol''"""

    @staticmethod
    @abstractmethod
    def name() -> str:
        """Needs to return the sub command name
            something like
            return helpers.mod_name(__file__)
        """

    @staticmethod
    @abstractmethod
    def setup(sub_cmd: argparse.ArgumentParser) -> None:
        """ The setup methode is supposed to add all command options
        and set the run methode as the _func_ attribute of the sub_cmd

        """
        ...

    @staticmethod
    @abstractmethod
    def run(parsed_args: argparse.Namespace, other_args: List[str]) -> bool:
        """ A sub command is called with known and unknown args
        """
        ...
        return False
