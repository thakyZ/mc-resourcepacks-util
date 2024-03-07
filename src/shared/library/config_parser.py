#!/usr/bin/env python3

# pylint: disable=line-too-long,too-few-public-methods,broad-exception-caught
# cSpell:word dunder, resourcepack, resourcepacks, mcmeta, Gson

"""Temporary Module Docstring."""

import json

from .script_arguments import ScriptArguments
from .utils import list_append_many
from .resourcepack import ResourcePack


def read_from_options(args: ScriptArguments) -> tuple[list[ResourcePack], list[ResourcePack]]:
    """Read resourcepacks and incompatible resourcepacks from ``options.txt`` file.

    Args:
        args (ScriptArguments): The arguments from the script CLI.
    """
    output: tuple[list[ResourcePack], list[ResourcePack]] = ([], [])
    with args.options_file.open(encoding="utf8") as mc_options:
        for line in mc_options.readlines():
            if line.startswith("resourcePacks:"):
                list_append_many(output[0], ResourcePack.from_list(json.loads(line.removeprefix("resourcePacks:")), args=args))
            if line.startswith("incompatibleResourcePacks:"):
                list_append_many(output[1], ResourcePack.from_list(json.loads(line.removeprefix("incompatibleResourcePacks:")), args=args))
        mc_options.close()
    return output

def read_builtin_from_options(args: ScriptArguments) -> tuple[list[ResourcePack], list[ResourcePack]]:
    output: tuple[list[ResourcePack], list[ResourcePack]] = ([], [])
    with args.options_file.open(encoding="utf8") as mc_options:
        for line in mc_options.readlines():
            if line.startswith("resourcePacks:"):
                list_append_many(output[0], ResourcePack.from_list(json.loads(line.removeprefix("resourcePacks:")), args=args))
            if line.startswith("incompatibleResourcePacks:"):
                list_append_many(output[1], ResourcePack.from_list(json.loads(line.removeprefix("incompatibleResourcePacks:")), args=args))
        mc_options.close()
    return output
