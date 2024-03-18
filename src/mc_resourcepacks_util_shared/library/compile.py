#!/usr/bin/python3

"""A module used to compile """

import os
from pathlib import Path
import tempfile
from typing import Any

from .utils import list_has
from .script_arguments import ScriptArguments
from .logger import pprint, quit_with_error
from .resourcepack import ResourcePack
from .dir_file_utils import check_if_dir_exists_create


def json_default(obj: Any) -> Any:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        obj (Any): _description_

    Raises:
        TypeError: If the type of the argument ``obj`` is not.

    Returns:
        Any: _description_
    """
    if isinstance(obj, ResourcePack):
        return obj.config_string
    raise TypeError(f"Type of obj is not a valid type got, {type(obj)}.")


def compile_with_save(
    args: ScriptArguments, enabled: list[ResourcePack], incompatible: list[ResourcePack]
) -> None:
    """Compiles the resourcepacks selected in ``enabled.txt`` and writes them to ``options.txt``.

    Args:
        args (ScriptArguments): The arguments from the script CLI.
        enabled (list[ResourcePack]): The current static list of enabled resourcepacks.
        incompatible (list[ResourcePack]): The current static list of enabled incompatible resourcepacks.
    """
    try:
        temp_json: str = ""
        # open the source file normally
        with args.options_file.open(mode="r+", encoding="utf8") as mc_options_source:
            try:
                # make a hidden tempfile to stage your changes in
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".txt",
                    prefix=".",
                    dir=args.minecraft_folder,
                    encoding="utf8",
                    delete=False,
                ) as mc_options_target:
                    # iterate over lines in the source file (each line ends with \n)
                    for line in mc_options_source.readlines():
                        if line.startswith("resourcePacks:"):
                            # do any edits here, and then call target.write
                            temp_json = ResourcePack.from_list(enabled)
                            mc_options_target.write(f"resourcePacks:{temp_json}\n")
                        elif line.startswith("incompatibleResourcePacks:"):
                            # do any edits here, and then call target.write
                            temp_json = ResourcePack.from_list(incompatible)
                            mc_options_target.write(
                                f"incompatibleResourcePacks:{temp_json}\n"
                            )
                        else:
                            mc_options_target.write(line)
                    mc_options_source.close()
                    mc_options_target.close()
                    try:
                        # now swap the edited copy into place
                        if os.path.exists(args.options_file):
                            os.replace(mc_options_target.name, args.options_file)
                        else:
                            os.rename(mc_options_target.name, args.options_file)
                    except BaseException as exception:
                        quit_with_error(exception)
            # tempfile tries to delete the temporary file, but it's gone now
            except FileNotFoundError as file_not_found_error:
                quit_with_error(file_not_found_error)
    except FileNotFoundError as file_not_found_error:
        quit_with_error(file_not_found_error)


def compile_without_save(
    args: ScriptArguments,
    enabled: list[ResourcePack],
    incompatible: list[ResourcePack],
    minimal: bool = False,
) -> str:
    """Compiles the resourcepacks selected in ``enabled.txt`` and writes them to ``options.txt``

    Args:
        args (ScriptArguments): The arguments from the script CLI
        enabled (list[ResourcePack]): The current static list of enabled resourcepacks
        incompatible (list[ResourcePack]): The current static list of enabled incompatible resourcepacks
        minimal (bool, optional): Whether or not to print minimal amount of data. Defaults to False.

    Returns:
        str: Output of the ``options.txt`` file.
    """
    new_output: str = ""
    temp_json: str = ""

    with Path(os.path.realpath(args.dir), "options.txt").open(
        "r", encoding="utf8"
    ) as mc_options_source:
        try:
            for line in mc_options_source.readlines():
                if line.startswith("resourcePacks:"):
                    temp_json = ResourcePack.from_list(enabled, False)
                    new_output += f"resourcePacks:{temp_json}\n"
                elif line.startswith("incompatibleResourcePacks:"):
                    temp_json = ResourcePack.from_list(incompatible, False)
                    new_output += f"incompatibleResourcePacks:{temp_json}\n"
                else:
                    if not minimal:
                        new_output += f"{line}"
            mc_options_source.close()
        except FileNotFoundError as file_not_found_error:
            quit_with_error(file_not_found_error)
    return new_output


def get_enabled_resourcepacks(args: ScriptArguments) -> list[ResourcePack]:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        args (ScriptArguments): The arguments from the script CLI.

    Returns:
        list[ResourcePack]: _description_.
    """
    enabled: list[ResourcePack] = []
    with Path(os.path.realpath(args.compile_dir), "enabled.txt").open(
        mode="r+", encoding="utf8"
    ) as enabled_file:
        for item in enabled_file.readlines():
            new_item: str = item.replace("\n", "")
            if new_item != "" and list_has(enabled, item):
                enabled.append(ResourcePack(new_item, args=args))
        enabled_file.close()
    return enabled


def compile_resourcepacks(
    args: ScriptArguments, enabled: list[ResourcePack], incompatible: list[ResourcePack]
) -> None:
    """Compiles all resource packs in the ``<dir>/../resource_packs/*.txt`` file into the ``<dir>/options.txt`` file.

    Args:
        args (ScriptArguments): The arguments from the script CLI
        enabled (list[ResourcePack]): The current list of enabled packs from the ``enabled.txt`` file.
        incompatible (list[ResourcePack]): The current list of enabled packs from parsing the ``resourcepacks`` directory.
    """
    check_if_dir_exists_create(args.compile_dir)
    # https://stackoverflow.com/a/71990118/1112800
    if args.save:
        compile_with_save(args, enabled, incompatible)
    else:
        output: str = compile_without_save(args, enabled, incompatible, args.minimal)
        pprint(output, level="none")
