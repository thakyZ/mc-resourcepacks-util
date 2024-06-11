#!/usr/bin/env python3

"""A module for resourcepack information"""

import zipfile
from zipfile import ZipFile
from pathlib import Path
from typing import Any, Generator, Literal

from .script_arguments import ScriptArguments
from .errors import ArgumentMissingError
from .pack_mcmeta import PackMcMeta
from .utils import escape_config_chars, open_file, try_decode_json_force, unescape_config_chars


enabled: list["ResourcePack"] = []


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
            return self.config_string == other.config_string and self.resourcepack_file == other.resourcepack_file and self.mcmeta_file == other.mcmeta_file
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
            if built_in_only and not pack.startswith("file"):
                resourcepacks.append(ResourcePack(pack, args=args))
            elif not built_in_only:
                resourcepacks.append(ResourcePack(pack, args=args))
        return resourcepacks

    @staticmethod
    def from_list(config_list: list["ResourcePack"], raw: bool = True) -> str:
        # TODO: Add method summary.
        # TODO: Add description for arguments/raises/returns.
        """_summary_

        Args:
            config_list (list[&quot;ResourcePack&quot;]): _description_
            raw (bool, optional): _description_. Defaults to True.

        Returns:
            str: _description_
        """
        def add_surrounding_quotes(arg: ResourcePack) -> str:
            output: str = "\""
            if raw:
                output += arg.raw_config_string.replace(r"\\", "\\")
            else:
                output += arg.config_string.replace(r"\\", "\\")
            output += "\""
            return output

        simple_list: list[str] = list(map(add_surrounding_quotes, config_list))
        str_config_list: str = f"[{','.join(simple_list)}]"
        return str_config_list

    @staticmethod
    def to_list_str(_list: list["ResourcePack"], short: bool = False, raw: bool = True) -> list[str]:
        # TODO: Add method summary.
        # TODO: Add description for arguments/raises/returns.
        """_summary_

        Args:
            _list (list[&quot;ResourcePack&quot;]): _description_
            short (bool, optional): _description_. Defaults to False.

        Returns:
            list[str]: _description_
        """
        output: list[str] = []
        for item in _list:
            if short is False:
                if raw is True:
                    output.append(item.raw_config_string)
                else:
                    output.append(item.config_string)
            else:
                output.append(item.resourcepack_file.name)
        return output

    @staticmethod
    def load_resource_packs(args: ScriptArguments) -> list["ResourcePack"]:
        """Creates a list of resourcepack data from a location from the arguments.

        Args:
            args (ScriptArguments): The arguments from the script CLI.

        Returns:
            list[ResourcePack]: A list of resourcepack data
        """
        # NOTE: These are imported while not on the top level, because of import recursion.
        # pylint: disable-next=C0415
        from .dir_file_utils import walk_level
        resourcepacks: list[ResourcePack] = []
        for root, directories, files in walk_level(args.resourcepacks_folder, level=0):
            for directory in directories:
                mcmeta_file: Path = Path(root, directory, "pack.mcmeta")
                if mcmeta_file.exists():
                    with open_file(mcmeta_file, mode="r") as mcmeta_dir_file:
                        resourcepack_data = ResourcePack(file=Path(root, directory), mcmeta=PackMcMeta(try_decode_json_force(mcmeta_dir_file.read())))
                        resourcepacks.append(resourcepack_data)
            for file in files:
                file_path: Path = Path(root, file)
                if zipfile.is_zipfile(file_path):
                    with ZipFile(file=file_path, mode="r", allowZip64=True) as zip_file:
                        for zipped_file in zip_file.namelist():
                            if zipped_file != "pack.mcmeta":
                                continue
                            with open_file(zipped_file, zip_file=zip_file, mode="r", force_zip64=True) as zipped_file_stream:
                                resourcepack_data = ResourcePack(file=file_path, mcmeta=PackMcMeta(try_decode_json_force(zipped_file_stream.read())))
                                resourcepacks.append(resourcepack_data)
        return resourcepacks
