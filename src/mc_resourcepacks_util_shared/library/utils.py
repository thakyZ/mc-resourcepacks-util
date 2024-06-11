#!/usr/bin/env python3

"""Utils to for this script."""

import os
import re
from re import Pattern, Match
import json
from json.decoder import JSONDecodeError
import io
from pathlib import Path
from typing import IO, Iterator, Literal, Type, TypeVar, Generic, Any, get_origin
from zipfile import ZipFile
import codecs
import chardet
from chardet import detect

from .logger import pprint
from .errors import EnvironmentVariableNotFoundError


T = TypeVar("T")


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
        return isinstance(obj, generic_type)  # type: ignore


def is_typeof(_type: Type[T], obj: Any | None) -> bool:
    """Returns if the type of ``obj`` is a the correct type of this type checker.

    Args:
        _type (Type[T]): A any type
        obj (Any | None): Any object of any type.

    Returns:
        bool: Returns ``True`` if the argument ``obj`` is of the type of the ``_type``.
    """
    if isinstance(obj, _type):
        assert isinstance(obj, _type)  # noinspection PyTypeHints
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


def list_append_many(_list: list[Any], other_list: list[Any]) -> list[Any]:
    """Appends many items to a single list.

    Args:
        _list (list[Any]): The first list to append to.
        other_list (list[Any]): The second list to get items to append with.

    Returns:
        list[Any]: Items of type _list with other_list appended.
    """
    output: list[Any] = _list
    for item in other_list:
        output.append(item)
    return output


def escape_config_chars(_json: str) -> str:
    """Escapes special unicode characters that would normally be escaped in Java Gson.

    Args:
        _json (str): The json string to escape the characters of.

    Returns:
        str: The json string with its invalid characters escaped.
    """
    output: str = _json
    output = output.replace("!", r"\u0021")
    output = output.replace('"', r"\u0022")
    output = output.replace("#", r"\u0023")
    output = output.replace("$", r"\u0024")
    output = output.replace("%", r"\u0025")
    output = output.replace("&", r"\u0026")
    output = output.replace("'", r"\u0027")
    output = output.replace("(", r"\u0028")
    output = output.replace(")", r"\u0029")
    output = output.replace("\u00a7", r"\u00a7")
    return output


def unescape_config_chars(_json: str) -> str:
    """Un-escapes special unicode characters that would normally be escaped in Java Gson.

    Args:
        _json (str): The json string to un-escape the characters of.

    Returns:
        str: The json string with its invalid characters un-escaped.
    """
    output: str = _json
    output = output.replace(r"\u0021", "!")
    output = output.replace(r"\u0022", '"')
    output = output.replace(r"\u0023", "#")
    output = output.replace(r"\u0024", "$")
    output = output.replace(r"\u0025", "%")
    output = output.replace(r"\u0026", "&")
    output = output.replace(r"\u0027", "'")
    output = output.replace(r"\u0028", "(")
    output = output.replace(r"\u0029", ")")
    output = output.replace(r"\u00a7", "\u00a7")
    return output


_ReadWriteMode = Literal[
    "w", "w+", "wb", "wb+", "r", "r+", "rb", "rb+", "a", "a+", "ab", "ab+"
]
_ReadWriteModeBasic = Literal["w", "r"]


def open_file(
    file: Path | str,
    mode: _ReadWriteMode | _ReadWriteModeBasic = "r",
    zip_file: ZipFile | None = None,
    force_zip64: bool = False,
) -> IO[Any]:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
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

    def simplify_mode(
        mode: _ReadWriteMode | _ReadWriteModeBasic,
    ) -> _ReadWriteModeBasic:
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
    zip_file_stream: IO[bytes] = zip_file.open(
        name=file, mode=simplify_mode(mode), force_zip64=force_zip64
    )
    if encoding is None:
        raise TypeError(f'Encoding type was not found for the file "{file}".')
    decoded_file_stream: IO[Any] = io.StringIO(
        zip_file_stream.read().decode(encoding=encoding)
    )
    return decoded_file_stream


_LINE_COLUMN_CHAR_REGEX: Pattern[str] = re.compile(
    r"Extra data: line (\d+) column (\d+) \(char (\d+)\)$", re.MULTILINE
)
_MULTI_LINE_ENSURE_REGEX: Pattern[str] = re.compile(
    r"^(?: |\t)*\"[^\r\n]+\": \"((?:[^\b\"]|\\.\r?\n)*)\",?$", re.MULTILINE
)


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

    def ensure_single_line_json_string(data: str) -> str:
        data = re.sub(r"\r?\n", r"\n", data, flags=0)
        cloned_data: str = data
        matches: Iterator[Match[str]] = _MULTI_LINE_ENSURE_REGEX.finditer(data)
        for _, match in enumerate(matches):
            for _, group in enumerate(match.groups()):
                new_string: str = re.sub(r"\r?\n", r"\\n", group, flags=0)
                new_string = re.sub(r"\t", r"\\t", new_string, flags=0)
                cloned_data = cloned_data.replace(group, new_string)
        return cloned_data

    def remove_extra_data(data: str, extra_data_position: int) -> dict[str, Any]:
        cloned_data: str = ""
        for index, line in enumerate(data.splitlines(True)):
            if index >= extra_data_position - 1:
                break
            cloned_data += line
        return json.loads(cloned_data)

    try:
        tmp_ensured: str = ensure_single_line_json_string(data)
        output = json.loads(tmp_ensured)
    except JSONDecodeError as json_decoder_error:
        error_msg: str = str(json_decoder_error)
        if "Extra data: " not in error_msg:
            raise json_decoder_error
        exception_msg: Match[str] | None = _LINE_COLUMN_CHAR_REGEX.search(error_msg)
        if exception_msg is None:
            raise json_decoder_error
        output = remove_extra_data(data, int(exception_msg.groups()[0]))
    except Exception as exception:
        raise exception
    except BaseException as base_exception:
        raise base_exception

    return output


def transform_env_variables(value: str) -> str:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        value (str): _description_

    Raises:
        EnvironmentVariableNotFoundError: _description_

    Returns:
        str: _description_
    """
    output: str = value
    unix_regex: Pattern[str] = re.compile(r"(\$[\w\d_]+)\b")
    pwsh_regex: Pattern[str] = re.compile(r"(\$env:[\w\d_]+)\b")
    batch_regex: Pattern[str] = re.compile(r"(\%[\w\d_]+\%)")

    unix_matches: Match[str] | None = unix_regex.search(output)
    pwsh_matches: Match[str] | None = pwsh_regex.search(output)
    batch_matches: Match[str] | None = batch_regex.search(output)

    env_var: str | None = None

    while (
        unix_matches is not None
        or pwsh_matches is not None
        or batch_matches is not None
    ):
        if unix_matches is not None:
            if os.name == "nt" and unix_matches.groups()[0] == "$HOME":
                output = value.replace(
                    unix_matches.groups()[0], os.path.expanduser("~")
                )
            elif os.name != "nt":
                env_var = os.environ.get(unix_matches.groups()[0].replace("$", ""))
                if env_var is not None:
                    output = value.replace(unix_matches.groups()[0], env_var)
                else:
                    raise EnvironmentVariableNotFoundError(
                        f'Environment variable by key, "{unix_matches.groups()[0]}" was not found on the system.'
                    )
        if pwsh_matches is not None:
            env_var = os.environ.get(pwsh_matches.groups()[0].replace("$env:", ""))
            if env_var is not None:
                output = value.replace(pwsh_matches.groups()[0], env_var)
            else:
                raise EnvironmentVariableNotFoundError(
                    f'Environment variable by key, "{pwsh_matches.groups()[0]}" was not found on the system.'
                )
        if batch_matches is not None:
            env_var = os.environ.get(
                batch_matches.groups()[0].removeprefix("%").removesuffix("%")
            )
            if env_var is not None:
                output = value.replace(batch_matches.groups()[0], env_var)
            else:
                raise EnvironmentVariableNotFoundError(
                    f'Environment variable by key, "{batch_matches.groups()[0]}" was not found on the system.'
                )
        unix_matches = unix_regex.search(output)
        pwsh_matches = pwsh_regex.search(output)
        batch_matches = batch_regex.search(output)
    return output


def check_if_regex_string(query: str) -> None | Pattern[str]:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        query (str): _description_

    Returns:
        None | Pattern[str]: _description_
    """
    try:
        return re.compile(rf"{query}")
    except re.error as re_error:
        pprint(re_error)
        return None
    # pylint: disable-next=W0718
    except BaseException as base:
        pprint(base)
        return None


def decode_bytes(value: bytes | bytearray) -> str | None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        value (bytes | bytearray): _description_

    Returns:
        str | None: _description_
    """
    try:
        encoding: str | None = detect(value)["encoding"]
        if encoding is None:
            return None
        decode: str = codecs.decode(value, encoding, "strict")
        return decode
    # pylint: disable-next=W0718
    except BaseException as base_exception:
        pprint(base_exception)
        return None
