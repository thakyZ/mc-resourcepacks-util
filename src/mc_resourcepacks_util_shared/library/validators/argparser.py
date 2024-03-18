#!/usr/bin/env python3

# TODO: Add Module Docstring.
"""_summary_"""

import os
from pathlib import Path

from ..logger import pprint
from ..constants import PathLike


def validate_resolve_path(value: str) -> PathLike:
    # TODO: Add method docstring.
    # TODO: Add method docstring description for args/raises/returns.
    """_summary_

    Args:
        value (str): _description_

    Returns:
        _PathLike: _description_
    """
    output: PathLike = value
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
