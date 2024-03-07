#!/usr/bin/env python3

# TODO: Add Module Docstring.
"""_summary_"""

import os
from os import PathLike
from pathlib import Path
import argparse
from argparse import ArgumentError, ArgumentTypeError

from ..logger import pprint

_PathLike = str | PathLike[str] | Path

def validate_resolve_path(value: str) -> _PathLike:
    # TODO: Add method docstring.
    # TODO: Add method docstring description for args/raises/returns.
    """_summary_

    Args:
        value (str): _description_

    Returns:
        _PathLike: _description_
    """
    output: _PathLike = value
    try:
        output = Path(os.path.realpath(value))
    # pylint: disable-next=W0718
    except BaseException as _exception:
        try:
            output = os.path.realpath(value)
        # pylint: disable-next=W0718
        except BaseException as exception:
            pprint(exception, level="exception")
        if output == value:
            pprint(_exception, level="exception")
    return output
