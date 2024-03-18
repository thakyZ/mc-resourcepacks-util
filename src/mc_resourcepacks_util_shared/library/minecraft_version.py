#!/usr/bin/env python3

# TODO: Add Module Docstring.
"""_summary_"""

import json
import os
from pathlib import Path
from ctypes import ArgumentError
from typing import Any, Generator, Literal, get_args

from .logger import pprint

from .script_arguments import ScriptArguments

from .errors import NotValidMcVersionError


class MinecraftVersion:
    # TODO: Add Method Docstring.
    """_summary_"""
    current_version: str = ""

    ResourcePackVersion = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

    ResourcePackVersionSchema: dict[ResourcePackVersion, list[str] | None] = {
        1: ["1.6", "1.6.1", "1.6.2", "1.6.4", "1.7", "1.7.2", "1.7.4", "1.7.5", "1.7.6", "1.7.7", "1.7.8", "1.7.9", "1.7.10", "1.8", "1.8.1", "1.8.2"],
        2: ["1.9", "1.9.1", "1.9.2", "1.9.3", "1.9.4", "1.10", "1.10.1", "1.10.2"],
        3: ["1.11", "1.11.1", "1.11.2", "1.12", "1.12.1", "1.12.2"],
        4: ["1.13", "1.13.1", "1.13.2", "1.14", "1.14.1", "1.14.2", "1.14.3", "1.14.4"],
        5: ["1.15", "1.15.1", "1.15.2", "1.16", "1.16.1"],
        6: ["1.16.2", "1.16.3", "1.16.4", "1.16.5"],
        7: ["1.17", "1.17.1"],
        8: ["1.18", "1.18.1", "1.18.2"],
        9: ["1.19", "1.19.1", "1.19.2"],
        10: None,
        11: [],
        12: ["1.19.3"],
        13: ["1.19.4"],
        14: [],
        15: ["1.20", "1.20.1"],
        16: [],
        17: [],
        18: ["1.20.2"]
    }

    def __init__(self, resource_pack_version: ResourcePackVersion | None = None, minecraft_version: str | None = None) -> None:
        _tmp_version: list[str] | None
        if resource_pack_version is None and minecraft_version is None:
            raise ArgumentError("One of resource_pack_version or minecraft_version must be specified.")
        if minecraft_version == "latest":
            _tmp_version = self.ResourcePackVersionSchema.get(get_args(self.ResourcePackVersion)[-1])
            if _tmp_version is None:
                raise ArithmeticError("Unable to find valid item in Resource Pack Version Schema.")
            self.current_version = _tmp_version[-1]
        elif minecraft_version:
            self.current_version = minecraft_version
        elif resource_pack_version:
            _tmp_version = self.ResourcePackVersionSchema[resource_pack_version]
            if _tmp_version is None:
                raise ArithmeticError("Unable to find valid item in Resource Pack Version Schema.")
            self.current_version = _tmp_version[-1]

    def pack_version(self) -> ResourcePackVersion:
        """Get's version of the minecraft pack.

        Raises:
            NotValidMcVersionError: If the pack version cannot be determined.

        Returns:
            ResourcePackVersion: A valid resource pack version.
        """
        output: MinecraftVersion.ResourcePackVersion | None = None
        for version, mc_versions in MinecraftVersion.ResourcePackVersionSchema.items():
            if mc_versions is None:
                continue
            for mc_version in mc_versions:
                if mc_version == self.current_version:
                    output = version
        if output is None:
            raise NotValidMcVersionError(f"Minecraft version specified is not valid: {self.current_version}")
        return output

    @staticmethod
    def get_valid_versions() -> list[str]:
        """Gets a list of valid minecraft versions.

        Returns:
            list[str]: A list of valid minecraft versions.
        """
        output: list[str] = []
        for _, mcmeta_list in MinecraftVersion.ResourcePackVersionSchema.items():
            if mcmeta_list is not None:
                for version in mcmeta_list:
                    output.append(version)
        output.append("latest")
        return output

    def __repr__(self) -> str:
        return f"current_version = {self.current_version} | pack_version = {self.pack_version()}"

    def __rich_repr__(self) -> Generator[tuple[Literal["current_version"], str] | tuple[Literal["pack_version"], ResourcePackVersion], Any, None]:
        yield "current_version", self.current_version
        yield "pack_version", self.pack_version()


def determine_current_mc_version(args: ScriptArguments) -> MinecraftVersion | None:
    # TODO: Add description for method returns/raises/arguments.
    """Determines the current minecraft version based off of the directory specified in the script arguments.

    Args:
        args (ScriptArguments): The script arguments

    Raises:
        NotValidMcVersionError: Throws an error if the

    Returns:
        MinecraftVersion | None: _description_
    """
    if args.minecraft_version in MinecraftVersion.get_valid_versions():
        return MinecraftVersion(minecraft_version=args.minecraft_version)
    mmc_pack_json_path: Path = Path(os.path.realpath(args.dir), "..", "mmc-pack.json").resolve()
    #instance_cfg_path: Path = Path(os.path.realpath(args.dir), "..", "instance.cfg")
    output: None | MinecraftVersion = None
    if mmc_pack_json_path.exists():
        with mmc_pack_json_path.open(mode="r", encoding="utf8") as mmc_pack_json_file:
            data: dict[str, Any] = json.loads(mmc_pack_json_file.read())
            for key_t1, value_t1 in data.items():
                if key_t1 == "components":
                    if isinstance(value_t1, list):
                        for _, component in enumerate(value_t1):
                            if isinstance(component, dict) and component["cachedName"].lower() == "minecraft":
                                output = MinecraftVersion(minecraft_version=component["version"])
    #elif instance_cfg_path.exists():
    #    with instance_cfg_path.open(mode="r", encoding="utf8") as instance_cfg_file:
    #        for cfg_line in instance_cfg_file.readlines():
    #
    else:
        raise NotValidMcVersionError("")
    return output
