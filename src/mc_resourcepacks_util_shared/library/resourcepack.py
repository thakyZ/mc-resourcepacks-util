#!/usr/bin/env python3

"""A module for resourcepack information"""

import zipfile
from zipfile import ZipFile
from pathlib import Path
from typing import Any, Callable, Generator, Literal

from .logger import pprint

from .script_arguments import ScriptArguments
from .errors import ArgumentMissingError
from .dir_file_utils import walk_level
from .pack_mcmeta import PackMcMeta
from .utils import escape_config_chars, open_file, try_decode_json_force, unescape_config_chars


class ResourcePack():
    """A resourcepack data class."""
    config_string: str = ""
    raw_config_string: str = ""
    resourcepack_file: Path
    mcmeta_file: PackMcMeta | None = None

    def __init__(self, file: str | Path, mcmeta: PackMcMeta | None = None, args: ScriptArguments | None = None) -> None:
        if isinstance(file, Path):
            if mcmeta is None:
                self.mcmeta_file = self.__mcmeta_from_unsafe_path__(file)
            else:
                self.mcmeta_file = mcmeta
            self.resourcepack_file = file
            self.raw_config_string = f"file/{escape_config_chars(file.name)}"
            self.config_string = f"file/{unescape_config_chars(file.name)}"
        else:
            if args is None:
                raise ArgumentMissingError("Must supply argument ``args`` if argument ``file`` is typeof string.")
            self.resourcepack_file = Path(args.resourcepacks_folder, unescape_config_chars(file.removeprefix("file/")))
            self.raw_config_string = escape_config_chars(file)
            self.config_string = unescape_config_chars(file)
            if mcmeta is None:
                self.mcmeta_file = self.__mcmeta_from_unsafe_path__(self.resourcepack_file)
            else:
                self.mcmeta_file = mcmeta

    @property
    def __encoding__(self) -> str:
        return self._encoding

    @__encoding__.setter
    def __encoding__(self, value: str) -> None:
        self._encoding = value

    def __set_encoding__(self, value: str) -> None:
        self.__encoding__ = value

    def __mcmeta_from_unsafe_path__(self, file: Path) -> PackMcMeta | None:
        if zipfile.is_zipfile(file):
            with ZipFile(file=file, mode="r", allowZip64=True) as zip_file:
                for zipped_file in zip_file.namelist():
                    if zipped_file != "pack.mcmeta":
                        continue
                    with open_file(zipped_file, mode="r", zip_file=zip_file, force_zip64=True) as zipped_file_stream:
                        return PackMcMeta(try_decode_json_force(zipped_file_stream.read()))
        elif file.is_dir():
            mcmeta_file: Path = Path(file, "pack.mcmeta")
            if mcmeta_file.exists():
                with open_file(file=mcmeta_file, mode="r") as mcmeta_dir_file:
                    return PackMcMeta(try_decode_json_force(mcmeta_dir_file.read()))
        return None

    def __has_attr__(self, key: str) -> bool:
        return key in self.__dict__

    def __get_attr__(self, key: str) -> Any:
        return self.__dict__[key]

    def __repr__(self) -> str:
        return self.raw_config_string

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ResourcePack):
            return (self.config_string == other.config_string and
                    self.resourcepack_file == other.resourcepack_file and
                    self.mcmeta_file == other.mcmeta_file)
        if isinstance(other, str):
            return self.config_string == other.removesuffix("\n")
        if isinstance(other, Path):
            return self.resourcepack_file == other
        if isinstance(other, PackMcMeta):
            return self.mcmeta_file == other
        return False

    def __rich_repr__(self) -> Generator[tuple[Literal["config_string"], str] | tuple[Literal["raw_config_string"], str] | tuple[Literal["resourcepack_file"], Path] | tuple[Literal["mcmeta_file"], PackMcMeta | None], Any, None]:
        yield "config_string", self.config_string
        yield "raw_config_string", self.raw_config_string
        yield "resourcepack_file", self.resourcepack_file
        yield "mcmeta_file", self.mcmeta_file

    @staticmethod
    def to_list(config_list: str, args: ScriptArguments, built_in_only: bool = False) -> list["ResourcePack"]:
        """Creates a list of resourcepack data from a json list.

        Args:
            json_object (Any): A json list.
            args (ScriptArguments): The arguments from the script CLI.

        Returns:
            list[ResourcePack]: A list of resourcepack data
        """
        resourcepacks: list[ResourcePack] = []

        list_config_list: list[str] = config_list.removeprefix("[\"").removesuffix("\"]").split("\",\"")
        for _, pack in enumerate(list_config_list):
            if isinstance(pack, str):
                if built_in_only and not pack.startswith("file"):
                    resourcepacks.append(ResourcePack(pack, args=args))
                elif not built_in_only:
                    resourcepacks.append(ResourcePack(pack, args=args))
        return resourcepacks

    @staticmethod
    def from_list(config_list: list["ResourcePack"], raw: bool = True) -> str:
        """_summary_

        Args:
            config_list (list[&quot;ResourcePack&quot;]): _description_
            raw (bool, optional): _description_. Defaults to True.

        Returns:
            str: _description_
        """
        def __add_surrounding_quotes__(arg: ResourcePack) -> str:
            output: str = "\""
            if raw:
                output += arg.raw_config_string.replace(r"\\", "\\")
            else:
                output += arg.config_string.replace(r"\\", "\\")
            output += "\""
            return output

        simple_list: list[str] = list(map(__add_surrounding_quotes__, config_list))
        str_config_list: str = f"[{','.join(simple_list)}]"
        return str_config_list

    @staticmethod
    def load_resource_packs(args: ScriptArguments) -> list["ResourcePack"]:
        """Creates a list of resourcepack data from a location from the arguments.

        Args:
            args (ScriptArguments): The arguments from the script CLI.

        Returns:
            list[ResourcePack]: A list of resourcepack data
        """
        resourcepacks: list[ResourcePack] = []
        mcmeta: PackMcMeta
        for root, directories, files in walk_level(args.resourcepacks_folder, level=0):
            for directory in directories:
                resourcepack_file: Path = Path(root, directory)
                mcmeta_file: Path = Path(resourcepack_file, "pack.mcmeta")
                if mcmeta_file.exists():
                    with open_file(mcmeta_file, mode="r") as mcmeta_dir_file:
                        mcmeta = PackMcMeta(try_decode_json_force(mcmeta_dir_file.read()))
                        resourcepack_data = ResourcePack(file=resourcepack_file, mcmeta=mcmeta)
                        resourcepacks.append(resourcepack_data)
            for file in files:
                file_path: Path = Path(root, file)
                if zipfile.is_zipfile(file_path):
                    with ZipFile(file=file_path, mode="r", allowZip64=True) as zip_file:
                        for zipped_file in zip_file.namelist():
                            if zipped_file != "pack.mcmeta":
                                continue
                            with open_file(zipped_file, zip_file=zip_file, mode="r", force_zip64=True) as zipped_file_stream:
                                mcmeta = PackMcMeta(try_decode_json_force(zipped_file_stream.read()))
                                resourcepack_data = ResourcePack(file=file_path, mcmeta=mcmeta)
                                resourcepacks.append(resourcepack_data)
        return resourcepacks
