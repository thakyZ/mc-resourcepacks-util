#!/usr/bin/python3

# TODO: Add module summary.
"""_summary_"""

import os
import re
from pathlib import Path
from typing import Any, Generator

from .logger import quit_with_message, print_found_query
from .query_builder import QueryBuilder


def walk_and_talk(branches: list[str], trunk: Path | str, root: Path | str, query_builder: QueryBuilder, temp: Path | str | None = None) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        branches (list[str]): _description_
        trunk (Path | str): _description_
        root (Path | str): _description_
        query_builder (QueryBuilder): _description_
        temp (Path | str | None, optional): _description_. Defaults to None.
    """
    trim_trunk: Path | str = trunk
    if temp is not None:
        trim_trunk = temp
    for branch in branches:
        if re.match(query_builder.query, f"{Path(trunk, branch)}") is not None:
            print_found_query(Path(root), Path(trim_trunk, branch))


def walk_level(some_dir: str | Path, level: int = 1) -> Generator[tuple[str, list[str], list[str]], Any, None]:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        some_dir (str): _description_
        level (int, optional): _description_. Defaults to 1.

    Yields:
        Generator[tuple[str, list[str], list[str]], Any, None]: _description_
    """
    if isinstance(some_dir, str):
        some_dir = Path(some_dir)
    _some_dir: tuple[str, ...] = some_dir.parts
    assert some_dir.is_dir()
    num_sep: int = len(_some_dir) - 1
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this: int = len(Path(root).parts) - 1
        if num_sep + level <= num_sep_this:
            del dirs[:]


def check_if_dir_exists_create(_dir: str | Path) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
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
