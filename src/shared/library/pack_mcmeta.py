#!/usr/bin/python3

# pylint: disable=line-too-long,too-few-public-methods,broad-exception-caught
# cSpell:word dunder, resourcepack, resourcepacks, mcmeta, Gson

"""A module containing data from the resourcepack's ``pack.mcmeta`` file."""

from typing import Any, Generator, Literal

class PackMcMeta:
    """Data from the pack.mcmeta file.

    JSON schema of pack.mcmeta

    ```json-schema
    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
        "pack": {
            "type": "object",
            "properties": {
                "pack_format": {
                    "minimum": 0,
                    "type": "integer",
                    "exclusiveMinimum": true
                },
                "description": {
                    "type": "string"
                }
            }
        }
    }
    ```
    """
    pack_format: int = -1
    description: str = ""
    is_valid: bool = False

    def __init__(self, data: dict[str, Any]) -> None:
        if "pack" in data.keys():
            pack: dict[str, Any] = data["pack"]
            if "pack_format" in pack.keys() and isinstance(pack["pack_format"], int) and pack["pack_format"] > 0:
                self.pack_format = pack["pack_format"]
                self.is_valid |= True
            if "description" in pack.keys() and isinstance(pack["description"], str):
                self.description = pack["description"]
                self.is_valid |= True

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PackMcMeta):
            return False
        return (other.description == self.description and
                other.pack_format == self.pack_format and
                other.is_valid == self.is_valid)

    def __rich_repr__(self) -> Generator[tuple[Literal["pack_format"], int] | tuple[Literal["description"], str] | tuple[Literal["is_valid"], bool], Any, None]:
        yield "pack_format", self.pack_format
        yield "description", self.description
        yield "is_valid", self.is_valid
