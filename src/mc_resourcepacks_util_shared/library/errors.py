#!/usr/bin/env python3

"""Module Containing Custom Errors."""


class NotValidRegexError(Exception):
    # TODO: Add class summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        Exception (_type_): _description_
    """


class FileNotReadError(Exception):
    # TODO: Add class summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        Exception (_type_): _description_
    """


class EnvironmentVariableNotFoundError(Exception):
    # TODO: Add class summary.
    # TODO: Add description for arguments/raises/returns.
    """_summary_

    Args:
        Exception (_type_): _description_
    """


class FailedToLoadDataError(Exception):
    # TODO: Add class summary.
    # TODO: Add description for arguments/raises/returns.
    """Error when a task to load data had failed.

    Args:
        Exception (_type_): _description_
    """


class NotYetImplementedError(Exception):
    # TODO: Add class summary.
    # TODO: Add description for arguments/raises/returns.
    """Error when a task is run and not yet implemented.

    Args:
        Exception (_type_): _description_
    """


class ArgumentMissingError(Exception):
    # TODO: Add class summary.
    # TODO: Add description for arguments/raises/returns.
    """Error when a argument is not specified when needed.

    Args:
        Exception (_type_): _description_
    """


class NotValidMcVersionError(Exception):
    # TODO: Add class summary.
    # TODO: Add description for arguments/raises/returns.
    """Error when the version specified was not valid.

    Args:
        Exception (_type_): _description_
    """
