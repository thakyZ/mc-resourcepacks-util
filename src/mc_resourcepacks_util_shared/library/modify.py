#!/bin/env/python

# TODO: Add module docstring
"""_summary_"""

import os
from pathlib import Path
from typing import Any, Callable
from zipfile import ZipFile, ZIP_DEFLATED
import json
from json.decoder import JSONDecodeError
import tempfile

from .extensions.zip_data import ZipData, ZipDataInvalidError

from .errors import FileNotReadError

from .minecraft_version import MinecraftVersion

from .utils import decode_bytes_enc, encode_bytes, try_decode_json_force

from .logger import quit_with_error, pprint
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
                tmp: tuple[int, str] = tempfile.mkstemp(dir=root)
                os.close(tmp[0])
                data: ZipData = ZipData("", "", None)
                tmp_file: Path = Path(root, tmp[1])
                success: bool = False
                pack_version = minecraft_version.pack_version()
                with ZipFile(file_path, mode="r", allowZip64=True) as z_in:
                    with ZipFile(tmp_file, mode="w", allowZip64=True) as z_out:
                        for item in z_in.infolist():
                            if item.filename != "pack.mcmeta":
                                z_out.writestr(item, z_in.read(item.filename))
                            else:
                                decoded: tuple[str | None, str | None] = (None, None)
                                cfr: bytes = z_in.read(item.filename)
                                decoded = decode_bytes_enc(cfr)
                                if decoded[0] is None or decoded[1] is None:
                                    z_in.close()
                                    z_out.close()
                                    raise FileNotReadError(f"File at the path {item.filename} in zip file {file_path} has not been read.")
                                data = ZipData(item.filename, decoded[0], decoded[1])
                                try:
                                    json_data: dict[str, Any] = try_decode_json_force(data.text)
                                    if json_data["pack"]["pack_format"] != pack_version:
                                        json_data["pack"]["pack_format"] = pack_version
                                        json_text: str = json.dumps(json_data, indent=4)
                                        data = ZipData(item.filename, json_text, decoded[1])
                                        success = True
                                except JSONDecodeError:
                                    pprint("file_path     = ", file_path)
                                    pprint("item.filename = ", item.filename)
                                    pprint("decoded[0]    = ", decoded[0])
                                    raise
                        z_out.close()
                    z_in.close()
                if success:
                    if not data.is_valid():
                        raise ZipDataInvalidError(f"Zip data for zip file at {file_path} is invalid.", data)
                    test: bool = True
                    # replace with the temp archive
                    if not test:
                        os.remove(file_path)
                    else:
                        os.rename(file_path, file_path.with_name(f"{file_path.name}.bak"))
                    os.rename(tmp_file, file_path)
                    with ZipFile(file_path, mode="a", allowZip64=True, compression=ZIP_DEFLATED) as z_app:
                        try:
                            cfw: bytes | None = encode_bytes(data.text, data.encoding)
                            if cfw is not None:
                                z_app.writestr("pack.mcmeta", cfw)
                            else:
                                raise Exception("a1")
                        except BaseException as error:
                            z_app.close()
                            quit_with_error(error)
                        z_app.close()
                else:
                    os.remove(tmp_file)
