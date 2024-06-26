#!/bin/env/python

# TODO: Add module docstring
"""_summary_"""

import os
from pathlib import Path
from typing import Literal, Callable
from zipfile import ZipFile
import json

from .extensions.zip_data import ZipData

from .errors import FileNotReadError

from .minecraft_version import MinecraftVersion

from .utils import decode_bytes_enc, encode_bytes

from .logger import pprint
from .script_arguments import ScriptArguments


def list_map(_list: list[str], root: str) -> list[Path]:
    # TODO: Add module docstring
    """_summary_

    Args:
        list (_type_): _description_
        Ttype (_type_): _description_

    Returns:
        list[T]: _description_
    """
    output: list[Path] = []
    for item in _list:
        output.append(Path(root, item))
    return output


def list_contains(_list: list[Path], predicate: Callable[[Path], bool]) -> bool:
    """_summary_

    Args:
        list (_type_): _description_
        Callable (_type_): _description_

    Returns:
        bool: _description_
    """
    for item in _list:
        if predicate(item):
            return True
    return False


def modify_resourcepacks(args: ScriptArguments, minecraft_version: MinecraftVersion) -> None:
    # TODO: Add method summary.
    """_summary_

    Args:
        args (ScriptArguments): _description_
        enabled (list[ResourcePack]): _description_
        incompatible (list[ResourcePack]): _description_
    """
    for root, directories, files in os.walk(os.path.realpath(args.resourcepacks_folder)):
        all_dirs_with_meta_or_zip: list[Path] = []
        for directory in directories:
            if Path(root, directory, "pack.mcmeta").exists():
                all_dirs_with_meta_or_zip.append(Path(root, directory, "pack.mcmeta"))
            else:
                dir_items: list[str] = os.listdir(Path(root, directory))
                dir_paths: list[Path] = list_map(dir_items, root)
                if list_contains(dir_paths, lambda x: x.is_file() and x.suffix == ".zip"):
                    all_dirs_with_meta_or_zip.append(Path(root, directory))
        for file in files:
            if list_contains(all_dirs_with_meta_or_zip, lambda x: x.is_dir() and root in str(x)):
                continue
            file_path: Path = Path(root, file)
            if file_path.suffix == ".zip":
                file_to_modify: list[ZipData] = []
                with ZipFile(file_path, mode="r", allowZip64=True) as zipped_file:
                    for compressed_file in zipped_file.namelist():
                        if compressed_file == "pack.mcmeta":
                            decoded: tuple[str | None, str | None] = (None, None)
                            with zipped_file.open(compressed_file, mode="r", force_zip64=True) as cfr:
                                data: bytes = cfr.read()
                                decoded = decode_bytes_enc(data)
                                cfr.close()
                            if decoded[0] is None or decoded[1] is None:
                                raise FileNotReadError(f"File at the path {compressed_file} in zip file {file} has not been read.")
                            json_data: dict[Literal["pack"], dict[Literal["pack_format"] | Literal["description"], str | int]] = json.loads(decoded[0])
                            json_data["pack"]["pack_format"] = minecraft_version.pack_version()
                            json_text: str = json.dumps(json_data, indent=4)
                            file_to_modify.append(ZipData(compressed_file, json_text, decoded[1]))
                with ZipFile(file_path, mode="w", allowZip64=True) as zipped_file:
                    for compressed_file in zipped_file.namelist():
                        for file_data in file_to_modify:
                            if file_data.file == compressed_file:
                                with zipped_file.open(compressed_file, mode="w", force_zip64=True) as cfw:
                                    encoded: bytes | None = encode_bytes(file_data.text, file_data.encoding)
                                    if encoded is not None:
                                        cfw.write(encoded)
                                    cfw.close()
