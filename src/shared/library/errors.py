#!/usr/bin/env python3

# pylint: disable=line-too-long,too-few-public-methods,broad-exception-caught
# cSpell:word dunder, resourcepack, resourcepacks, mcmeta, Gson

"""Module Containing Custom Errors."""

class FailedToLoadDataError(Exception):
    """Error when a task to load data had failed."""


class NotYetImplementedError(Exception):
    """Error when a task is run and not yet implemented."""


class ArgumentMissingError(Exception):
    """Error when a argument is not specified when needed."""


class NotValidMcVersionError(Exception):
    """Error when the version specified was not valid."""
