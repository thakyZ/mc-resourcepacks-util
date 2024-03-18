#!/usr/bin/env python3

"""Module containing extensions of other classes."""

import os
from argparse import Namespace
from pathlib import Path
from types import NotImplementedType
from typing import Any

from .logger import pprint

class ScriptArguments():
    """A custom extensions of the ``argparse`` ``Namespace`` class."""

    @property
    def minecraft_folder(self) -> Path:
        """Gets the path to the minecraft folder.

        Returns:
            Path: Path to the minecraft folder.
        """
        return self._minecraft_folder

    @property
    def options_file(self) -> Path:
        """Gets the path to the options file.

        Returns:
            Path: Path to the options file.
        """
        return self._options_file

    @property
    def resourcepacks_folder(self) -> Path:
        """Gets the path to the resourcepacks folder.

        Returns:
            Path: Path to the resourcepacks folder.
        """
        return self._resourcepacks_folder

    @property
    def config_folder(self) -> Path:
        """Gets the path to the compile/decompile config folder.

        Returns:
            Path: Path to the compile/decompile config folder.
        """
        return self._config_folder

    def __init__(self, namespace: Namespace) -> None:
        for key, value in namespace.__dict__.items():
            self.__setattr__(key, value)
        if self.__contains__("dir") and self.dir is not None and isinstance(self.dir, str | Path):
            self._minecraft_folder: Path = self.__get_minecraft_dir__(self.dir)
            self._options_file: Path = Path(self.minecraft_folder, "options.txt")
            self._resourcepacks_folder: Path = Path(self.minecraft_folder, "resourcepacks")
            self._config_folder: Path
            if self.__contains__("compile") and self.compile is True and self.compile_dir is not None and isinstance(self.compile_dir, str | Path):
                self._config_folder = self.__determine_config_dir__(_dir=self.compile_dir)
            elif self.__contains__("decompile") and self.decompile is True and self.decompile_dir is not None and isinstance(self.decompile_dir, str | Path):
                self._config_folder = self.__determine_config_dir__(_dir=self.decompile_dir)
            else:
                self._config_folder = self.__determine_config_dir__(path=self.minecraft_folder)

    def __determine_config_dir__(self, path: Path | None = None, _dir: str | Path | None = None) -> Path:
        # pylint: disable-next=R1702
        if path is not None:
            if path.parent.name not in ["Local", "LocalLow", "Roaming"]:
                for directory in path.parent.iterdir():
                    if directory.is_dir():
                        for other_directory in directory.iterdir():
                            if not self.__test_if_is_minecraft_dir__(other_directory):
                                return Path(path.parent, "resourcepacks")
            if not Path(os.getcwd(), "resourcepacks").exists():
                return Path(os.getcwd(), "resourcepacks")
            if not Path(os.path.dirname(os.path.realpath(__file__)), "resourcepacks"):
                return Path(os.path.dirname(os.path.realpath(__file__)), "resourcepacks")
        if _dir is not None:
            return Path(_dir)
        raise FileNotFoundError("Path specified was not a valid minecraft directory.")

    def __get_minecraft_dir__(self, path: str | Path) -> Path:
        _path: Path = Path(os.path.realpath(path))
        if self.__test_if_is_minecraft_dir__(_path):
            return _path
        raise FileNotFoundError("Path specified was not a valid minecraft directory.")

    def __test_if_is_minecraft_dir__(self, path: Path) -> bool:
        if path.name in ["minecraft",".minecraft"]:
            return True
        if Path(path, "options.txt").exists() and Path(path, "resourcepacks").exists():
            return True
        return False

    def _get_kwargs(self) -> list[tuple[str, Any]]:
        return list(self.__dict__.items())

    def _get_args(self) -> list[Any]:
        return []

    def __eq__(self, other: Any) -> NotImplementedType | bool:
        if not isinstance(other, Namespace):
            return NotImplemented
        return vars(self) == vars(other)

    def __contains__(self, __name: str) -> bool:
        return __name in self.__dict__

    def __getattr__(self, __name: str):  # -> Any
        """
        NOTE: This has been purposefully left untyped so that it can be more than a single type let
              alone `Any`.
        """
        return self.__dict__[__name]

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.__dict__[__name] = __value
