#!/usr/bin/python3

# TODO: Add module summary.
"""_summary_"""

from argparse import ArgumentParser
import sys
import os
import traceback
import re
from re import Match, Pattern
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, Union, Iterable, NoReturn

from rich import inspect
from rich.prompt import Prompt as RichPrompt, PromptError
from rich.console import Console
from rich.theme import Theme
from rich.text import TextType
from rich.style import StyleType

from .errors import ArgumentMissingError


STYLES: dict[str, StyleType] = {"a": ""}

THEME: Theme = Theme(styles=STYLES, inherit=True)

CONSOLE: Console = Console(
    color_system="windows",
    force_terminal=True,
    force_jupyter=False,
    force_interactive=True,
    soft_wrap=True,
    theme=THEME,
    stderr=False,
    file=None,
    quiet=False,
    no_color=False,
    tab_size=4,
    legacy_windows=False,
)

LogLevel = Union[
    Literal["debug"],
    Literal["none"],
    Literal["inspect"],
    Literal["info"],
    Literal["warn"],
    Literal["error"],
    Literal["exception"],
    Literal["parser_error"],
]


# pylint: disable-next=R0913
def pprint(
    *objects: Any,
    level: LogLevel = "info",
    new_line_start: bool = False,
    show_locals: bool = False,
    suppress: Iterable[str | ModuleType] = (),
    _help: bool = False,
    methods: bool = False,
    docs: bool = True,
    private: bool = False,
    dunder: bool = False,
    sort: bool = True,
    _all: bool = False,
    value: bool = True,
    parser: ArgumentParser | None = None,
) -> None:
    """A rich print wrapper.

    Args:
        level (LogLevel, optional): The level to log at. Defaults to "info".
        new_line_start (bool, optional): Adds a newline at the start of the log message. Defaults to ``False``.
        show_locals (bool, optional): Enable display of local variables. Defaults to ``False``.
        suppress (Iterable[Union[str, ModuleType]], optional): Optional sequence of modules or paths to exclude from traceback. Defaults to ``()``.
        _help (bool, optional): Show full help text rather than just first paragraph. Defaults to ``False``.
        methods (bool, optional): Enable inspection of callables. Defaults to ``False``.
        docs (bool, optional): Also render doc strings. Defaults to ``True``.
        private (bool, optional): Show private attributes (beginning with underscore). Defaults to ``False``.
        dunder (bool, optional): Show attributes starting with double underscore. Defaults to ``False``.
        sort (bool, optional): Sort attributes alphabetically. Defaults to ``True``.
        _all (bool, optional): Show all attributes. Defaults to ``False``.
        new_line_start (bool, False): Insert a new line at the start if the output contains more than one line. Defaults to ``False``.
    """
    string_builder: str = ""
    if level == "none":
        CONSOLE.print(*objects, new_line_start=new_line_start)
    elif level == "exception":
        CONSOLE.print_exception(width=None, show_locals=show_locals, suppress=suppress)
    elif level == "inspect":
        inspect(
            objects,
            console=CONSOLE,
            help=_help,
            methods=methods,
            docs=docs,
            private=private,
            dunder=dunder,
            sort=sort,
            all=_all,
            value=value,
        )
    elif level == "parser_error":
        if parser is None:
            raise ArgumentMissingError(
                'Argument <parser> is required to have a valid argument parser if level is "parser_error"'
            )
        for _, item in enumerate(objects):
            string_builder += str(item)
        parser.error(string_builder)
    else:
        level_prefix: str = "[[blue]INF[/blue]]"
        if level == "debug":
            level_prefix = "[[gray]DBG[/gray]]"
        if level == "warn":
            level_prefix = "[[yellow]WRN[/yellow]]"
        if level == "error":
            level_prefix = "[[red]ERR[/red]]"
        CONSOLE.print(level_prefix, end=" ", new_line_start=False)
        CONSOLE.print(*objects, new_line_start=new_line_start)


def prompt(
    _prompt: TextType = "",
    *,
    password: bool = False,
    choices: list[str] | None = None,
    show_default: bool = True,
    show_choices: bool = True,
) -> str:
    """Prompt the user for a response.

    Args:
        prompt (TextType, optional): The question to ask the user. Defaults to "".
        password (bool, optional): Determines if this prompt response is a password, and will censor it in console. Defaults to False.
        choices (List[str] | None, optional): A list of choices to provide and check against. Defaults to None.
        show_default (bool, optional): Show the default option. Defaults to True.
        show_choices (bool, optional): Show the list of choices. Defaults to True.
    """
    try:
        rich_prompt: RichPrompt = RichPrompt(
            prompt=_prompt,
            console=CONSOLE,
            password=password,
            choices=choices,
            show_default=show_default,
            show_choices=show_choices,
        )
        value: str = rich_prompt.ask(
            prompt=_prompt,
            console=CONSOLE,
            password=password,
            choices=choices,
            show_default=show_default,
            show_choices=show_choices,
        )
        if choices is not None and not rich_prompt.check_choice(value):
            raise PromptError(
                f'Submitted value from prompt, "{value}" is not a valid choice.'
            )
        return value
    except KeyboardInterrupt:
        CONSOLE.print()
        sys.exit(0)


class BColors:
    """Old Unix Console Color Class
    NOTE: This class is no longer needed
    """

    HEADER = "\033[95m"
    OK_BLUE = "\033[94m"
    OK_CYAN = "\033[96m"
    OK_GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END_COLOR = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def quit_with_message(msg: str) -> NoReturn:
    """Quit the script with a message.

    Args:
        msg (str): The message to quit with.

    Returns:
        NoReturn: Quits and doesn't continue the script.
    """
    pprint(f"[red]{msg}[/red]", level="error")
    sys.exit(0)


def quit_with_error(exception: BaseException) -> NoReturn:
    """Quits the script with an ``Error`` or ``BaseException``

    Args:
        exception (BaseException): A typeof ``Error`` or any ``Exception``/``Error`` derived from ``BaseException``.

    Returns:
        NoReturn: Quits and doesn't continue the script.
    """
    line_pattern: Pattern[str] = re.compile(r"(.*)(line \d+)(.*)")
    reason_pattern: Pattern[str] = re.compile(r"(.*): (.*)")
    inner_line_pattern: Pattern[str] = re.compile(r" *\^+ *?")
    for note in traceback.format_exception(exception):
        for _line in note.split("\n"):
            matched_line: Match[str] | None = line_pattern.match(_line)
            matched_reason: Match[str] | None = reason_pattern.match(_line)
            if inner_line_pattern.match(_line):
                pprint(f"[dark_red]{_line}[/dark_red]", level="exception")
            elif matched_line:
                pprint(
                    f"{matched_line.groups().index(0)}[dark_red]{matched_line.groups()[1]}[/dark_red]{matched_line.groups()[2]}",
                    level="exception",
                )
            elif matched_reason:
                pprint(
                    f"[dark_red]{matched_reason.groups()[0]}[/dark_red]: {matched_reason.groups()[1]}",
                    level="exception",
                )
            else:
                pprint(_line, level="exception")
    sys.exit(1)


def print_error(msg: str | BaseException) -> None:
    # TODO: Add method summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        msg (str | BaseException): _description_
    """
    pprint(f"[red]{msg}[/red]")


def print_found_query(_file: str | Path, _path: str | Path) -> None:
    """Prints information that the script has found a query.

    Args:
        _file (str | Path): The found file in the query.
        _path (str | Path): The path of the file on the query.
    """
    new_path: Path | str
    if isinstance(_path, str):
        try:
            new_path = Path.resolve(Path(_path), strict=True)
        except BaseException as base_exception:
            pprint(base_exception)
            new_path = _path.replace(os.path.sep, "/")
    else:
        new_path = _path
    new_file_path: str
    if isinstance(_file, Path):
        new_file_path = _file.name
    else:
        new_file_path = _file
    pprint(f"[blue]{new_file_path}[/blue] -> [green]{new_path}[/green]", level="info")


def print_found_query_bool(_file: str | Path, _path: str | Path, test: bool) -> None:
    # TODO: Add description for arguments/raises/returns.
    """Prints information that the script has found a query.

    Args:
        _file (str): The found file in the query.
        _path (str): _description_
        test (bool): _description_
    """
    new_path: Path | str
    if isinstance(_path, str):
        try:
            new_path = Path.resolve(Path(_path), strict=True)
        except BaseException as base_exception:
            print_error(base_exception)
            new_path = _path.replace(os.path.sep, "/")
    else:
        new_path = _path
    new_file_path: str
    if isinstance(_file, Path):
        new_file_path = _file.name
    else:
        new_file_path = _file
    tested: str = "[bold red]False[/bold red]"
    if test:
        tested = "[bold green]True[/bold green]"
    pprint(
        f"[blue]{new_file_path}[/blue] -> [green]{new_path}[/green] [white bold]([/white bold]{tested}[white bold])[/white bold]",
        level="info",
    )
