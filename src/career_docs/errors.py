"""Errors that the CLI prints and turns into a nonzero exit code."""


class CareerDocsError(Exception):
    """A validation or rendering failure with a user-facing message."""
