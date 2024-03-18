#!/usr/bin/python3
# coding=utf8

# TODO: Add module summary.
"""_summary_"""

import os
from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import Literal

from mc_resourcepacks_util_shared.library.logger import quit_with_message
from mc_resourcepacks_util_shared.library.utils import transform_env_variables
from mc_resourcepacks_util_shared.library.query import parse_files
from mc_resourcepacks_util_shared.library.query_builder import QueryBuilder


def main() -> None:
    # TODO: Add method summary.
    """_summary_"""
    cwd: str = os.getcwd()

    parser: ArgumentParser = ArgumentParser(prog="Resourcepack Query Tools", description="Queries minecraft assets folders for files that match the query.", allow_abbrev=True)
    parser.add_argument("instance",                                                   type=str,            help="The first target directory.")  # noqa: E241
    parser.add_argument("query",                                                      type=str,            help="The relative, full, or partial path to search")  # noqa: E241
    parser.add_argument("--resourcepacks",          "-r", dest="query_resourcepacks", action="store_true", help="Uses the resource packs folder")  # noqa: E241
    parser.add_argument("--mods",                   "-m", dest="query_mods",          action="store_true", help="Uses the resource packs folder")  # noqa: E241
    parser.add_argument("--emissive_check",         "-e", dest="is_emissive_check",   action="store_true", help="Emissive Suffix Consistency Check. Checks to see if all files are matching consistency with the specific query suffix.")  # noqa: E241
    parser.add_argument("--instances_dir", "--dir", "-d", dest="instances_dir",       type=str,            help="Specifies a custom instances directory.", default="")  # noqa: E241
    parser.add_argument("--regex",                  "-R", dest="is_regex",            action="store_true", help="Specifies that the query is using regex.")  # noqa: E241

    args: Namespace = parser.parse_args()

    emissive_check: Literal["emissive"] | None = None

    if args.is_emissive_check:
        emissive_check = "emissive"

    query_builder: QueryBuilder = QueryBuilder(query=args.query, regex=args.is_regex, parameter=emissive_check)

    path_one: Path = Path()

    if args.instances_dir != "":
        instances_dir: str = transform_env_variables(args.instances_dir)
        path_one = Path(instances_dir, args.instance)
    else:
        path_one = Path(cwd, args.instance)

    if not path_one.exists():
        quit_with_message("The <dir> parameter must exist on path.")
    elif not path_one.is_dir():
        quit_with_message("The <dir> parameter must be a directory.")

    dir_query: list[Path] = []
    ext_query: list[str] = []

    if args.query_resourcepacks is True:
        dir_query.append(Path(path_one, "minecraft", "resourcepacks"))
        ext_query.append(".zip")
        ext_query.append("dir")
    if args.query_mods is True:
        dir_query.append(Path(path_one, "minecraft", "mods"))
        ext_query.append(".jar")

    parse_files(ext_query, dir_query, query_builder)
