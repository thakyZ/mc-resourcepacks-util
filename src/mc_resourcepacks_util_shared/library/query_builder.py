#!/usr/bin/env python3
# coding=utf8

"""_summary_"""

import re
from re import Pattern
from typing import Literal

from .logger import quit_with_error
from .errors import NotValidRegexError
from .utils import check_if_regex_string


class QueryBuilder:
    """_summary_"""
    query: Pattern[str]
    patch: str = ""
    is_emissive_check: bool = False

    def __init__(self, query: str, regex: bool = False, parameter: Literal["emissive"] | None = None) -> None:
        test: Pattern[str] | None = None
        if regex:
            test = check_if_regex_string(query)
            if test is not None:
                self.query = test
            else:
                quit_with_error(NotValidRegexError(f"The regex pattern, {query} is not a valid regex."))
        else:
            test = check_if_regex_string(re.escape(query))
            if test is not None:
                self.query = test
            else:
                quit_with_error(NotValidRegexError(f"The regex pattern, {query} is not a valid regex."))
        if parameter is not None:
            self.patch = "emissive"
        if parameter is not None and regex is False:
            if not query.startswith("_"):
                self.query = re.compile(f"_{re.escape(query)}")
            else:
                self.query = re.compile(re.escape(query))
            self.is_emissive_check = True

    def to_list(self) -> list[str]:
        """_summary_

        Returns:
            list[str]: _description_
        """
        return [str(self.patch or ''), str(self.query)]

    def __repr__(self) -> str:
        return f"{str(self.patch or '')}{str(self.query)}"
