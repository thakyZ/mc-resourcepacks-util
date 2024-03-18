#!/usr/bin/python3

# TODO: Add module summary.
"""_summary_"""

import os
from pathlib import Path

from .script_arguments import ScriptArguments

from .resourcepack import ResourcePack

from .logger import pprint
from .dir_file_utils import check_if_dir_exists_create


def decompile_resourcepacks(args: ScriptArguments, enabled: list[ResourcePack], disabled: list[ResourcePack]) -> None:
    """Decompiles the resourcepacks selected in ``options.txt``

    Args:
        args (ScriptArguments): The arguments from the script CLI.
        enabled (list[ResourcePack]): The current static list of enabled resourcepacks.
        disabled (list[ResourcePack]): The current static list of non-enabled resourcepacks.
    """
    check_if_dir_exists_create(args.config_folder)
    for item in enabled:
        if "Â§" in item.config_string:
            pprint(item)
    with Path(os.path.join(os.path.realpath(args.config_folder), "enabled.txt")).open("wt+", -1, "utf8") as enabled_file:
        for item in enabled:
            enabled_file.write(f"{item.config_string}\n")
        enabled_file.close()
    with Path(os.path.join(os.path.realpath(args.config_folder), "disabled.txt")).open("wt+", -1, "utf8") as disabled_file:
        for item in disabled:
            disabled_file.write(f"{item.config_string}\n")
        disabled_file.close()
