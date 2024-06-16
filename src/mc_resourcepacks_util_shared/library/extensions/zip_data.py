#!/usr/bin/env python3

# TODO: Add module docstring.
"""_summary_"""

from pathlib import Path


class ZipData():
    # TODO: Add class docstring.
    """_summary_"""
    def __init__(self, file: str | Path, text: str, encoding: str | None) -> None:
        self.file = file
        self.text = text
        if encoding is not None:
            self.encoding = encoding
        else:
            self.encoding = "utf-8"

    @property
    def text(self) -> str:
        # TODO: Add method docstring.
        """_summary_

        Returns:
            str: _description_
        """
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        # TODO: Add method docstring.
        """_summary_

        Args:
            value (str): _description_
        """
        self._text: str = value

    @property
    def file(self) -> str | Path:
        # TODO: Add method docstring.
        """_summary_

        Returns:
            str | Path: _description_
        """
        return self._file

    @file.setter
    def file(self, value: str | Path) -> None:
        # TODO: Add method docstring.
        """_summary_

        Args:
            value (str | Path): _description_
        """
        self._file: str | Path = value

    @property
    def encoding(self) -> str:
        # TODO: Add method docstring.
        """_summary_

        Returns:
            str: _description_
        """
        return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        # TODO: Add method docstring.
        """_summary_

        Args:
            value (str): _description_
        """
        self._encoding: str = value
