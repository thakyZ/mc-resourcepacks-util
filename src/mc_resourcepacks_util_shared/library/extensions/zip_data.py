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

    def is_valid(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        return (((isinstance(self.file, str) and self.file != "") or (isinstance(self.file, Path) and self.file.exists())) and self.text != "" and self.encoding != "")

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


class ZipDataInvalidError(Exception):
    # TODO: Add class summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        Exception (_type_): _description_
    """
    def __init__(self, msg: str, data: ZipData, *args: object) -> None:
        super().__init__(msg, args)
        self.add_note(self.get_note_str(data))

    def get_note_str(self, data: ZipData) -> str:
        """_summary_

        Args:
            data (ZipData): _description_

        Returns:
            str: _description_
        """

        sb: str = f"typeof data.file   = {type(data.file)}\n"
        if isinstance(data.file, str):
            sb += f"data.file == \"\"    = {data.file == ""}\n"
        else:
            sb += f"data.file.exists() = {data.file.exists()}\n"
        sb += f"data.text == \"\"    = {data.text == ""}\n"
        sb += f"data.encoding      = {data.encoding}"
        return sb
