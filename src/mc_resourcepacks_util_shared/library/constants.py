#!/usr/bin/env python3
# coding=utf8

# TODO: Add module summary.
"""_summary_"""

from os import PathLike as _PathLike
from pathlib import Path
import re
from re import Pattern

script_directory: Path = Path.resolve(Path(__file__)).parent.absolute()

command_regex: Pattern[str] = re.compile(r"suffix\.emissive=(_?\w+)\\?r?\\?n?")

emissive_check_regex: Pattern[str] = re.compile(r"emissive_\w")

PathLike = str | _PathLike[str] | Path
