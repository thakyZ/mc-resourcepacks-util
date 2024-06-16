#!/usr/bin/env python3

"""Custom Class"""

from argparse import Action as _Action, HelpFormatter as _HelpFormatter
import re as _re
from re import Pattern as _Pattern
from typing import Any as _Any, Iterable as _Iterable


class CHelpFormatter(_HelpFormatter):
    """Custom formatter for generating help messages.

    Original Doc:
    Formatter for generating usage messages and argument help strings.

    Only the name of this class is considered a public API. All the methods
    provided by the class are considered an implementation detail.
    """

    # pylint: disable-next=W0231,W0511,W0246
    def __init__(self,
                 prog: str,
                 indent_increment: int = 2,
                 max_help_position: int = 24,
                 width: int | None = None) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)

    # ========================
    # Message building methods
    # ========================
    # pylint: disable-next=W0246
    def start_section(self, heading: str | None) -> None:
        # TODO: Add method summary.
        """_summary_

        Args:
            heading (str | None): _description_
        """
        super().start_section(heading)

    # pylint: disable-next=W0246
    def end_section(self) -> None:
        # TODO: Add method summary.
        """_summary_"""
        super().end_section()

    # pylint: disable-next=W0246
    def add_text(self, text: str | None) -> None:
        # TODO: Add method summary.
        """_summary_

        Args:
            text (str | None): _description_
        """
        super().add_text(text)

    # pylint: disable-next=W0246
    def add_usage(self,
                  usage: str | None,
                  actions: _Iterable[_Action],
                  groups: _Iterable[_Any],
                  prefix: str | None = None) -> None:
        # TODO: Add method summary.
        """_summary_

        Args:
            usage (str | None): _description_
            actions (_Iterable[_Action]): _description_
            groups (_Iterable[_Any]): _description_
            prefix (str | None, optional): _description_. Defaults to None.
        """
        super().add_usage(usage, actions, groups, prefix)

    # pylint: disable-next=W0246
    def add_argument(self, action: _Action) -> None:
        # TODO: Add method summary.
        """_summary_

        Args:
            action (_Action): _description_
        """
        super().add_argument(action)

    # pylint: disable-next=W0246
    def add_arguments(self, actions: _Iterable[_Action]) -> None:
        # TODO: Add method summary.
        """_summary_

        Args:
            actions (_Iterable[_Action]): _description_
        """
        super().add_arguments(actions)

    def _remove_version_monstrosity(self, text: str) -> str:
        pat: str = r"(--\w+_version \{)(?:\d+\.\d+(?:\.\d+)?,)*latest(\})"
        pattern: _Pattern[str] = _re.compile(pat, flags=_re.MULTILINE | _re.IGNORECASE)
        output: str = pattern.sub(r"\1#.#, #.#.#, latest\2", text)
        return output

    # =======================
    # Help-formatting methods
    # =======================
    # pylint: disable-next=W0246
    def format_help(self) -> str:
        # TODO: Add method summary.
        """_summary_

        Returns:
            str: _description_
        """
        _help: str = self._root_section.format_help()
        _help = self._remove_version_monstrosity(_help)
        if _help:
            _help = self._long_break_matcher.sub('\n\n', _help)
            _help = _help.strip('\n') + '\n'
        return _help
