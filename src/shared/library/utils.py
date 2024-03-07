#!/usr/bin/env python3

# pylint: disable=line-too-long,too-few-public-methods,broad-exception-caught
# cSpell:word dunder, resourcepack, resourcepacks, mcmeta, Gson, Gson, chardet, resultdict

"""Utils to for this script."""

import re
from re import Pattern, Match
import json
from json.decoder import JSONDecodeError
import io
from pathlib import Path
from typing import IO, Iterator, Literal, Type, TypeVar, Generic, Any, get_origin
from zipfile import ZipFile
import chardet

T = TypeVar('T')

# pylint: disable-next=R0903
class MyTypeChecker(Generic[T]):
    """A type checker class for any generic type and their subtypes.

    Args:
        Generic (T): A generic type with it's generic type parameters.
    """
    def is_right_type(self, obj: Any | None) -> bool:
        """Returns if the type of ``obj`` is a the correct type of this type checker.

        Args:
            obj (Any | None): Any object of any type.

        Returns:
            bool: Returns ``True`` if the argument ``obj`` is of the type of this generic class.
        """
        original_class: Any | None = get_origin(self)
        if original_class is None:
            return obj is None
        class_arguments: list[Any] | Any = original_class.__args__
        generic_type: Any = class_arguments[0]
        return isinstance(obj, generic_type) # type: ignore


def is_typeof(_type: Type[T], obj: Any | None) -> bool:
    """Returns if the type of ``obj`` is a the correct type of this type checker.

    Args:
        _type (Type[T]): A any type
        obj (Any | None): Any object of any type.

    Returns:
        bool: Returns ``True`` if the argument ``obj`` is of the type of the ``_type``.
    """
    if isinstance(obj, _type):
        assert isinstance(obj, _type) # noinspection PyTypeHints
        return True
    return False


def list_has(_list: list[Any], query: Any) -> bool:
    """Checks if the specified list has the specified query.

    Args:
        _list (list[Any]): The list of items to query.
        query (Any): The item to match in the list, literally.

    Returns:
        bool: Returns True if the list contains the specified query.
    """
    # NOTE: These are imported while not on the top level, because of import recursion.
    # pylint: disable-next=C0415
    from .pack_mcmeta import PackMcMeta
    # pylint: disable-next=C0415
    from .resourcepack import ResourcePack

    for _, item in enumerate(_list):
        if isinstance(item, ResourcePack):
            if isinstance(query, str):
                if query.startswith("file/"):
                    return query == item.config_string
            elif isinstance(query, Path):
                return query == item.resourcepack_file
            elif isinstance(query, PackMcMeta):
                return query == item.mcmeta_file
    return False


def list_append_many(_list: list[Any], other_list: list[Any]) -> None:
    """Appends many items to a single list.

    Args:
        _list (list[Any]): The first list to append to.
        other_list (list[Any]): The second list to get items to append with.
    """
    for item in other_list:
        _list.append(item)


def escaped_config_chars(_json: str) -> str:
    """Escapes special unicode characters that would normally be escaped in Java Gson.

    Args:
        _json (str): The json string to escape the characters of.

    Returns:
        str: The json string with its invalid characters escaped.
    """
    output: str = _json
    output = output.replace("!", "\\u0021")
    output = output.replace("\\\"", "\\u0022")
    output = output.replace("#", "\\u0023")
    output = output.replace("$", "\\u0024")
    output = output.replace("%", "\\u0025")
    output = output.replace("&", "\\u0026")
    output = output.replace("'", "\\u0027")
    output = output.replace("(", "\\u0028")
    output = output.replace(")", "\\u0029")
    output = output.replace("\u00a7", "\\u00a7")
    return output


def unescaped_config_chars(_json: str) -> str:
    """Un-escapes special unicode characters that would normally be escaped in Java Gson.

    Args:
        _json (str): The json string to un-escape the characters of.

    Returns:
        str: The json string with its invalid characters un-escaped.
    """
    output: str = _json
    output = output.replace("\\u0021", "!")
    output = output.replace("\\u0022", "\\\"")
    output = output.replace("\\u0023", "#")
    output = output.replace("\\u0024", "$")
    output = output.replace("\\u0025", "%")
    output = output.replace("\\u0026", "&")
    output = output.replace("\\u0027", "'")
    output = output.replace("\\u0028", "(")
    output = output.replace("\\u0029", ")")
    output = output.replace("\\u00a7",  "\u00a7")
    return output

_ReadWriteMode = Literal["w", "w+", "wb", "wb+", "r", "r+", "rb", "rb+", "a", "a+", "ab", "ab+"]
_ReadWriteModeBasic = Literal["w", "r"]

def open_file(file: Path | str, mode: _ReadWriteMode | _ReadWriteModeBasic = "r", zip_file: ZipFile | None = None, force_zip64: bool = False) -> IO[Any]:
    # TODO: Add summary for method.
    # TODO: Add description for method returns/raises/arguments.
    """_summary_

    Args:
        file (Path | str): _description_
        mode (_ReadWriteMode | _ReadWriteModeBasic, optional): _description_. Defaults to "r".
        zip_file (ZipFile | None, optional): _description_. Defaults to None.
        force_zip64 (bool, optional): _description_. Defaults to False.

    Raises:
        TypeError: _description_
        TypeError: _description_

    Returns:
        IO[Any]: _description_
    """
    def __simplify_mode__(mode: _ReadWriteMode | _ReadWriteModeBasic) -> _ReadWriteModeBasic:
        """Simplifies the mode parameter to be basic for zip file reading/writing.

        Args:
            mode (_ReadWriteMode | _ReadWriteModeBasic): The passed parameter mode.

        Returns:
            _ReadWriteModeBasic: The simplified mode parameter.
        """
        if mode.startswith("r"):
            return "r"
        return "w"

    raw_data: bytes
    encoding: str | None
    if zip_file is None:
        if not isinstance(file, Path):
            file = Path(file)
        with file.open(mode="rb") as tmp_read:
            raw_data = tmp_read.read()
            tmp_read.close()
        encoding = chardet.detect(raw_data)["encoding"]
        return file.open(mode=mode, encoding=encoding)
    if not isinstance(file, str):
        file = file.name
    with zip_file.open(name=file, mode="r", force_zip64=force_zip64) as tmp_read_zip:
        raw_data = tmp_read_zip.read()
        tmp_read_zip.close()
    encoding = chardet.detect(raw_data)["encoding"]
    zip_file_stream: IO[bytes] = zip_file.open(name=file, mode=__simplify_mode__(mode), force_zip64=force_zip64)
    if encoding is None:
        raise TypeError(f"Encoding type was not found for the file \"{file}\".")
    decoded_file_stream: IO[Any] = io.StringIO(zip_file_stream.read().decode(encoding=encoding))
    return decoded_file_stream


_LINE_COLUMN_CHAR_REGEX: Pattern[str] = re.compile(r"Extra data: line (\d+) column (\d+) \(char (\d+)\)$", re.MULTILINE)
_MULTI_LINE_ENSURE_REGEX: Pattern[str] = re.compile(r"^(?: |\t)*\"[^\r\n]+\": \"((?:[^\b\"]|\\.\r?\n)*)\",?$", re.MULTILINE)

def try_decode_json_force(data: str) -> dict[str, Any]:
    """Tries to decode a JSON file, if a specific error is returned it will parse it anyways,
    because I said so.

    Since some people cannot look up or don't know how to look up valid JSON comments, I personally
    had reached an issue where the JSON file had extra data at the end of the file that isn't
    machine readable.

    Args:
        data (str): The string containing a valid or not JSON object or array.

    Returns:
        dict[str, Any]: Outputs a JSON object or JSON list, based on the input.
    """
    output: dict[str, Any] = {}

    def __ensure_single_line_json_string__(data: str) -> str:
        data = re.sub(r"\r?\n", r"\n", data, flags=0)
        cloned_data: str = data
        matches: Iterator[Match[str]] = _MULTI_LINE_ENSURE_REGEX.finditer(data)
        for _, match in enumerate(matches):
            for _, group in enumerate(match.groups()):
                new_string: str = re.sub(r"\r?\n", r"\\n", group, flags=0)
                new_string = re.sub(r"\t", r"\\t", new_string, flags=0)
                cloned_data = cloned_data.replace(group, new_string)
        return cloned_data

    def __remove_extra_data__(data: str, extra_data_position: int) -> dict[str, Any]:
        cloned_data: str = ""
        for index, line in enumerate(data.splitlines(True)):
            if index >= extra_data_position - 1:
                break
            cloned_data += line
        return json.loads(cloned_data)

    try:
        tmp_ensured: str = __ensure_single_line_json_string__(data)
        output = json.loads(tmp_ensured)
    except JSONDecodeError as json_decoder_error:
        error_msg: str = str(json_decoder_error)
        if "Extra data: " not in error_msg:
            raise json_decoder_error
        exception_msg: Match[str] | None = _LINE_COLUMN_CHAR_REGEX.search(error_msg)
        if exception_msg is None:
            raise json_decoder_error
        output = __remove_extra_data__(data, int(exception_msg.groups()[0]))
    except Exception as exception:
        raise exception
    except BaseException as base_exception:
        raise base_exception

    return output
