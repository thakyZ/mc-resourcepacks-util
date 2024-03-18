#!/usr/bin/env python3

"""Temporary Module Docstring."""

from .script_arguments import ScriptArguments
from .resourcepack import ResourcePack


class ResourcePackTuple():
    # TODO: Add class summary.
    """_summary_"""

    _enabled: list[ResourcePack] | None = None
    _disabled: list[ResourcePack] | None = None
    _incompatible: list[ResourcePack] | None = None

    @property
    def enabled(self) -> list[ResourcePack]:
        # TODO: Add method summary.
        # TODO: Add description for arguments/raises/returns.
        """_summary_

        Returns:
            list[ResourcePack]: _description_
        """
        if self._enabled is not None:
            return self._enabled
        return []

    @enabled.setter
    def enabled(self, value: list[ResourcePack] | None) -> None:
        self._enabled = value

    @property
    def disabled(self) -> list[ResourcePack]:
        # TODO: Add method summary.
        # TODO: Add description for arguments/raises/returns.
        """_summary_

        Returns:
            list[ResourcePack]: _description_
        """
        if self._disabled is not None:
            return self._disabled
        return []

    @disabled.setter
    def disabled(self, value: list[ResourcePack] | None) -> None:
        self._disabled = value

    @property
    def incompatible(self) -> list[ResourcePack]:
        # TODO: Add method summary.
        # TODO: Add description for arguments/raises/returns.
        """_summary_

        Returns:
            list[ResourcePack]: _description_
        """
        if self._incompatible is not None:
            return self._incompatible
        return []

    @incompatible.setter
    def incompatible(self, value: list[ResourcePack] | None) -> None:
        self._incompatible = value


def read_from_options(args: ScriptArguments) -> ResourcePackTuple:
    # TODO: Add description for arguments/raises/returns.
    """Read resourcepacks and incompatible resourcepacks from ``options.txt`` file.

    Args:
        args (ScriptArguments): The arguments from the script CLI.

    Returns:
        ResourcePackTuple: _description_
    """
    output: ResourcePackTuple = ResourcePackTuple()
    with args.options_file.open(encoding="utf8") as mc_options:
        for line in mc_options.readlines():
            if line.startswith("resourcePacks:"):
                output.enabled = ResourcePack.to_list(line.removeprefix("resourcePacks:").removesuffix("\n"), args=args)
            if line.startswith("incompatibleResourcePacks:"):
                output.incompatible = ResourcePack.to_list(line.removeprefix("incompatibleResourcePacks:").removesuffix("\n"), args=args)
        mc_options.close()
    return output


def read_builtin_from_options(args: ScriptArguments) -> ResourcePackTuple:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        args (ScriptArguments): _description_

    Returns:
        ResourcePackTuple: _description_
    """
    output: ResourcePackTuple = ResourcePackTuple()
    with args.options_file.open(encoding="utf8") as mc_options:
        for line in mc_options.readlines():
            if line.startswith("resourcePacks:"):
                output.enabled = ResourcePack.to_list(line.removeprefix("resourcePacks:").removesuffix("\n"), args=args)
            if line.startswith("incompatibleResourcePacks:"):
                output.incompatible = ResourcePack.to_list(line.removeprefix("incompatibleResourcePacks:").removesuffix("\n"), args=args, built_in_only=True)
        mc_options.close()
    return output
