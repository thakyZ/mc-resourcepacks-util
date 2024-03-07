#!/usr/bin/python3

# pylint: disable=line-too-long,too-few-public-methods,broad-exception-caught
# cSpell:word dunder, resourcepack, resourcepacks, mcmeta, Gson

# TODO: Add Module Docstring.
"""_summary_"""

import os
from pathlib import Path
from typing import Any, Generator

from .logger import quit_with_message


def walk_level(some_dir: str | Path, level: int = 1) -> Generator[tuple[str, list[str], list[str]], Any, None]:
    # TODO: Add Method Docstring.
    # TODO: Add description for method returns/raises/arguments.
    """_summary_

    Args:
        some_dir (str): _description_
        level (int, optional): _description_. Defaults to 1.

    Yields:
        Generator[tuple[str, list[str], list[str]], Any, None]: _description_
    """
    some_dir = str(some_dir).rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, _files in os.walk(some_dir):
        yield root, dirs, _files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def check_if_dir_exists_create(_dir: str | Path) -> None:
    # TODO: Add Method Docstring.
    # TODO: Add description for method returns/raises/arguments.
    """_summary_

    Args:
        _dir (str): _description_
    """
    dir_pointer = Path(os.path.realpath(_dir))
    if not dir_pointer.exists():
        os.mkdir(dir_pointer)
    else:
        if not dir_pointer.is_dir():
            quit_with_message(f"Path specified at {_dir} already exists and is a file")
