#!/usr/bin/env python3
# coding=utf8

# TODO: Add module summary.
"""_summary_"""

import os
import re
from re import Match
from zipfile import ZipFile
from pathlib import Path

from .logger import pprint, print_found_query_bool, print_found_query, quit_with_error
from .query_builder import QueryBuilder
from .utils import decode_bytes
from .dir_file_utils import walk_and_talk, walk_level
from .constants import command_regex


def query_when_or_not_regex(
    leaf: Path | str,
    branch: Path | str,
    trunk: Path | str,
    query_builder: QueryBuilder,
    compressed: bool = False,
) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        leaf (Path | str): _description_
        branch (Path | str): _description_
        trunk (Path | str): _description_
        query_builder (QueryBuilder): _description_
        compressed (bool, optional): _description_. Defaults to False.
    """
    if compressed is False and isinstance(branch, Path):
        if query_builder.test(
            branch.as_posix(), resource_pack_item=Path(leaf).parts[-1]
        ):
            trunk = (
                str(branch).replace(str(leaf), "").removeprefix("/").removeprefix("\\")
            )
            print_found_query(leaf, trunk, compressed, False)
    else:
        if query_builder.test(str(branch), resource_pack_item=Path(leaf).parts[-1]):
            if compressed is False:
                trunk = (
                    str(branch)
                    .replace(str(leaf), "")
                    .removeprefix("/")
                    .removeprefix("\\")
                )
            print_found_query(leaf, trunk, compressed, False)


def test_match_of_opened_file(
    directory: Path | str,
    file: Path | str,
    line: str,
    query_builder: QueryBuilder,
    compressed: bool = False,
) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        directory (Path | str): _description_
        file (Path | str): _description_
        line (str): _description_
        query_builder (QueryBuilder): _description_
        compressed (bool, optional): _description_. Defaults to False.
    """
    matches: Match[str] | None = re.search(command_regex, line)
    if matches is not None:
        if compressed is False:
            file = (
                str(file)
                .replace(str(directory), "")
                .removeprefix("/")
                .removeprefix("\\")
            )
        test: bool = matches.groups()[0] == query_builder.query
        print_found_query_bool(directory, file, test, compressed, False)


def iterate_dir_ext(
    path: Path, directories: list[str], query_builder: QueryBuilder
) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        path (str): _description_
        directories (list[str]): _description_
        query_builder (QueryBuilder): _description_
    """
    for _directory in directories:
        directory: Path = Path(path, _directory)
        for _sub_path, sub_directories, sub_files in os.walk(directory):
            sub_path: Path = Path(_sub_path)
            for _sub_file in sub_files:
                sub_file: Path = Path(_sub_file)
                if query_builder.is_emissive_check:
                    if query_builder.patch in _sub_file:
                        with Path(sub_path, sub_file).open(mode="rb") as opened_file:
                            decoded: str | None = decode_bytes(opened_file.read())
                            if decoded is not None:
                                for line in decoded.splitlines(False):
                                    test_match_of_opened_file(
                                        directory, sub_file, line, query_builder
                                    )
                else:
                    query_when_or_not_regex(
                        directory, Path(sub_path, sub_file), sub_file, query_builder
                    )
            walk_and_talk(sub_directories, sub_path, directory, query_builder)


def iterate_file_ext(
    file_ext: str,
    path: Path,
    files: list[str],
    base_directory: Path,
    query_builder: QueryBuilder,
) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        file_ext (str): _description_
        path (str): _description_
        files (list[str]): _description_
        base_directory (Path): _description_
        query_builder (QueryBuilder): _description_
    """
    for _file in files:
        file: Path = Path(path, _file)
        try:
            if file.suffix == file_ext and path == base_directory:
                with ZipFile(
                    Path(path, file), mode="r", allowZip64=True
                ) as zipped_file:
                    for compressed_file in zipped_file.namelist():
                        if not os.path.isdir(compressed_file):
                            if query_builder.is_emissive_check:
                                if query_builder.patch in compressed_file:
                                    with zipped_file.open(
                                        compressed_file, mode="r", force_zip64=True
                                    ) as opened_compressed_file:
                                        decoded: str | None = decode_bytes(
                                            opened_compressed_file.read()
                                        )
                                        if decoded is not None:
                                            for line in decoded.splitlines(False):
                                                test_match_of_opened_file(
                                                    file,
                                                    compressed_file,
                                                    line,
                                                    query_builder,
                                                    compressed=True,
                                                )
                            else:
                                query_when_or_not_regex(
                                    file,
                                    compressed_file,
                                    compressed_file,
                                    query_builder,
                                    compressed=True,
                                )
                        else:
                            query_when_or_not_regex(
                                file,
                                compressed_file,
                                compressed_file,
                                query_builder,
                                compressed=True,
                            )
        # pylint: disable-next=W0718
        except BaseException as base_exception:
            quit_with_error(base_exception)


def iterate_dir_arg(
    file_exts: list[str], _dir: Path, query_builder: QueryBuilder
) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        file_exts (list[str]): _description_
        _dir (Path): _description_
        query_builder (QueryBuilder): _description_
    """
    for _path, directories, files in walk_level(_dir, 0):
        path: Path = Path(_path)
        for file_ext in file_exts:
            if file_ext == "dir":
                iterate_dir_ext(path, directories, query_builder)
            else:
                iterate_file_ext(file_ext, path, files, _dir, query_builder)


def parse_files(
    file_exts: list[str], directories: list[Path], query_builder: QueryBuilder
) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        file_exts (list[str]): _description_
        _dir (list[Path]): _description_
        query_builder (QueryBuilder): _description_
    """
    for directory in directories:
        iterate_dir_arg(file_exts, directory, query_builder)
