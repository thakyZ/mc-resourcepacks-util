#!/usr/bin/env python3

"""A module to clean temporary python cache directories/files."""

# region DO NOT EDIT THIS REGION
import os
from os import PathLike
import sys
from typing import Callable, Any, TypeAlias, NoReturn, Literal
from pathlib import Path
import shutil
from rich import print as pprint

# endregion

# region CONFIG REGION
DIRECTORIES_TO_REMOVE: list[str] = ["__pycache__", ".mypy_cache"]
FILE_TO_REMOVE: list[str] = []
# endregion

# region DO NOT EDIT THIS REGION
_OnExcCallback: TypeAlias = Callable[[Callable[..., Any], str, Exception], object]
StrOrBytesPath: TypeAlias = str | bytes | PathLike[str] | PathLike[bytes] | Path
FileSystemTypes: TypeAlias = Literal["file", "directory", "link", "hidden", "root"]


class FileTypeError(Exception):
    """Defines a custom error type that gets raised when the type of file/directory is unexpected."""

    def __init__(
        self,
        expected_type: FileSystemTypes,
        gotten_type: FileSystemTypes | None = None,
        msg: str | None = None,
    ) -> None:
        self.message: str | None = msg
        self.expected_type: FileSystemTypes = expected_type
        self.gotten_type: FileSystemTypes | None = gotten_type

    def __str__(self) -> str:
        string_builder: str = "Unexpected "
        if self.gotten_type is not None:
            string_builder += f"{self.gotten_type} expected {self.expected_type}"
        else:
            string_builder += f"filesystem item expected {self.expected_type}"
        if self.message is None:
            string_builder += f": {self.message}"
        return string_builder


def on_error(_: Callable[..., Any], message: str, exception: Exception) -> object:
    """On error function callback method.
    This is my first time using this so I do not know how to go about using this.

    Args:
        _ (Callable[..., Any]): Either the method os.lstat, os.open, os.close, os.rmdir, or
                                       os.path.islink
        message (str): The message passed from ``shutil.rmtree`` on execution.
        exception (Exception): The exception that is passed when the ``shutil.rmtree`` method fails.

    Returns:
        object: I don't know why it needs a return, it probably doesn't tho.
    """
    if exception:
        pprint(message)
        pprint(exception)
        sys.exit(1)
    else:
        pprint(message)
    return "soup"


_use_fd_functions: bool = (
    {os.open, os.stat, os.unlink, os.rmdir} <= os.supports_dir_fd
    and os.scandir in os.supports_fd
    and os.stat in os.supports_follow_symlinks
)


def unlink_wrapper(
    path: StrOrBytesPath,
    ignore_errors: bool = False,
    onexc: _OnExcCallback | None = None,
    dir_fd: int | None = None,
) -> None:
    """Wrapper for ``os.unlink`` to behave like ``shutil.rmtree`` in nature and arguments.

    Args:
        path (StrOrBytesPath): Path to the file in question.
        ignore_errors (bool, optional): Errors are ignored. Defaults to False.
        onexc (_OnExcCallback | None, optional): A callback that is called to handle the error with
            arguments ``(func, path, exc_info)`` where func is platform and implementation
            dependent; path is the argument to that function that caused it to fail; and the value
            of exc_info describes the exception. For onexc it is the exception instance.
            If ignore_errors is false and ``onexc`` is None, the exception is reraised.
            Defaults to None.
        dir_fd (int | None, optional): Should be a file descriptor open to a directory;
            path will then be relative to that directory.
            ``dir_fd`` may not be implemented on your platform.
            If it is unavailable, using it will raise a ``NotImplementedError``. Defaults to None.

    Raises:
        FileTypeError: Raises if the type of the filesystem item defined in ``path`` is not a file.
        NotImplementedError: Raises if the ``dir_fd`` is not None and not supported by the os.
    """
    if ignore_errors:
        # pylint: disable-next=W0613
        def _onexc_ignore(*args: Any) -> None:
            pass

        onexc = _onexc_ignore
    elif onexc is None:

        def _onexc_raise(*args: Any) -> NoReturn:
            # pylint: disable-next=E0704
            raise

        onexc = _onexc_raise

    if _use_fd_functions:
        try:
            if os.path.isfile(path):
                os.unlink(path, dir_fd=dir_fd)
            else:
                raise FileTypeError(expected_type="file")
        # pylint: disable-next=W0718
        except Exception as err:
            onexc(os.unlink, str(path), err)
    else:
        if dir_fd is not None:
            raise NotImplementedError("dir_fd unavailable on this platform")
        try:
            if os.path.isfile(path):
                os.unlink(path)
            else:
                raise FileTypeError(expected_type="file")
        # pylint: disable-next=W0718
        except Exception as err:
            onexc(os.unlink, str(path), err)


def main() -> None:
    """The main module method for this task."""
    this_script: str = os.path.realpath(__file__)
    script_path: str = os.path.dirname(this_script)
    vscode_path: Path = Path(script_path, "..")
    project_path: Path = Path(vscode_path, "..")

    for root, directories, files in os.walk(project_path):
        for _directory in directories:
            directory: Path = Path(root, _directory)
            if directory.is_dir() and directory.name in DIRECTORIES_TO_REMOVE:
                shutil.rmtree(path=directory, onexc=on_error)
        for _file in files:
            file: Path = Path(root, _file)
            if file.is_file() and file.name in FILE_TO_REMOVE:
                unlink_wrapper(path=file, onexc=on_error)


if __name__ == "__main__":
    main()
# endregion
