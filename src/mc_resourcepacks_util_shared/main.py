#!/usr/bin/python3

"""Main script module file."""

from .library.minecraft_version import MinecraftVersion
from .library.resourcepack import ResourcePack


def find_from_missing(enabled: list[ResourcePack], all_packs: list[ResourcePack]) -> list[ResourcePack]:
    """Gets the list of disabled resourcepacks from the list of enabled resourcepacks and what is in the ``resourcepacks`` folder.

    Args:
        enabled (list[ResourcePack]): List of currently enabled resourcepacks.
        all_packs (list[ResourcePack]): List of all existing resourcepacks.

    Returns:
        list[ResourcePack]: list of disabled resourcepacks.
    """
    disabled: list[ResourcePack] = []
    for pack in all_packs:
        if pack not in enabled:
            disabled.append(pack)
    return disabled


def filter_only_incompatible(packs: list[ResourcePack], mc_version: MinecraftVersion) -> list[ResourcePack]:
    # TODO: Add description for method returns/raises/arguments.
    """Filter each pack for a resourcepack that is incompatible.

    Args:
        packs (list[ResourcePack]): A list of resourcepacks.
        mc_version (MinecraftVersion): _description_.
    """
    incompatible: list[ResourcePack] = []
    for data in packs:
        if data.mcmeta_file is not None:
            if data.mcmeta_file.pack_format != mc_version.pack_version():
                incompatible.append(data)
    return incompatible
