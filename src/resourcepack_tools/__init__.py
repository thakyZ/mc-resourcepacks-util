#!/usr/bin/env python3

"""Initializer Module for CLI frontend"""

from argparse import ArgumentParser

from mc_resourcepacks_util_shared.main import filter_only_incompatible, find_from_missing
from mc_resourcepacks_util_shared.library.compile import compile_resourcepacks, get_enabled_resourcepacks
from mc_resourcepacks_util_shared.library.config_parser import ResourcePackTuple, read_builtin_from_options, read_from_options
from mc_resourcepacks_util_shared.library.decompile import decompile_resourcepacks
from mc_resourcepacks_util_shared.library.logger import pprint, prompt
from mc_resourcepacks_util_shared.library.minecraft_version import MinecraftVersion, determine_current_mc_version
from mc_resourcepacks_util_shared.library.resourcepack import ResourcePack
from mc_resourcepacks_util_shared.library.script_arguments import ScriptArguments
from mc_resourcepacks_util_shared.library.validators.argparser import validate_resolve_path
from mc_resourcepacks_util_shared.library.utils import list_append_many


def main() -> None:
    """Main script module file's method."""
    parser = ArgumentParser(description="Extracts and compiles a list of installed, enabled and disabled resource packs, inside the closest minecraft folder.")
    parser.add_argument("--dir", type=validate_resolve_path, help="Hard specify the nearest minecraft directory", default="./minecraft")
    parser.add_argument("--compile_dir", type=validate_resolve_path, help="The path to the directory to compile", default="./resourcepacks")
    parser.add_argument("--decompile_dir", type=validate_resolve_path, help="The path to output the compilation to.", default="./resourcepacks")
    parser.add_argument("--compile", action="store_true", help="Compiles the resource packs options.")
    parser.add_argument("--minimal", action="store_true", help="Output compile to console in a minimal capacity.")
    parser.add_argument("--decompile", action="store_true", help="Decompiles the resource packs options.")
    parser.add_argument("--save", action="store_true", help="Saves the compiled resource pack options to the `options.txt'")
    parser.add_argument("--minecraft_version", type=str, choices=MinecraftVersion.get_valid_versions(), help="Override the parsed minecraft version.")

    args: ScriptArguments = ScriptArguments(parser.parse_args())

    if args.minimal and args.compile is False:
        pprint("--minimal requires use of --compile", level="parser_error", parser=parser)
    elif args.minimal is True and args.compile is True and args.save is True:
        pprint("--minimal cannot be used with --save when use of --compile", level="parser_error", parser=parser)
    elif args.minimal is True and args.decompile is True:
        pprint("--minimal cannot be used with --decompile", level="parser_error", parser=parser)
    elif args.save is True and args.decompile is True:
        pprint("--save cannot be used with --decompile", level="parser_error", parser=parser)
    elif args.compile is True and args.decompile is True:
        pprint("--compile cannot be used with --decompile", level="parser_error", parser=parser)

    resourcepack_tuple: ResourcePackTuple
    resource_packs: list[ResourcePack] = ResourcePack.load_resource_packs(args)
    minecraft_version: MinecraftVersion | None = determine_current_mc_version(args)

    if minecraft_version is None:
        output: str = prompt("Unable to determine Minecraft version, which minecraft version are you using?", choices=MinecraftVersion.get_valid_versions(), show_choices=False)
        minecraft_version = MinecraftVersion(minecraft_version=output)

    if args.compile:
        resourcepack_tuple = read_builtin_from_options(args)
        resourcepack_tuple.enabled = get_enabled_resourcepacks(args)
        resourcepack_tuple.incompatible = list_append_many(resourcepack_tuple.incompatible, filter_only_incompatible(resourcepack_tuple.enabled, minecraft_version))
        compile_resourcepacks(args, resourcepack_tuple.enabled, resourcepack_tuple.incompatible)
    elif args.decompile:
        resourcepack_tuple = read_from_options(args)
        resourcepack_tuple.disabled = find_from_missing(resourcepack_tuple.enabled, resource_packs)
        decompile_resourcepacks(args, resourcepack_tuple.enabled, resourcepack_tuple.disabled)
    else:
        pprint("Failed to do task", level="error")
