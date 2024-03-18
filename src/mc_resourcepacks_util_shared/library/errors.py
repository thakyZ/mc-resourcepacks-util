#!/usr/bin/env python3

"""Module Containing Custom Errors."""


class NotValidRegexError(BaseException):
    """_summary_

    Args:
        BaseException (_type_): _description_
    """


class EnvironmentVariableNotFoundError(BaseException):
    """_summary_

    Args:
        BaseException (_type_): _description_
    """


class FailedToLoadDataError(Exception):
    """Error when a task to load data had failed.

    Args:
        Exception (_type_): _description_
    """


class NotYetImplementedError(Exception):
    """Error when a task is run and not yet implemented.

    Args:
        Exception (_type_): _description_
    """


class ArgumentMissingError(Exception):
    """Error when a argument is not specified when needed.

    Args:
        Exception (_type_): _description_
    """


class NotValidMcVersionError(Exception):
    """Error when the version specified was not valid.

    Args:
        Exception (_type_): _description_
    """
