"""RDAP exceptions."""
from __future__ import unicode_literals


class RdapError(Exception):
    """Base exception for RDAP errors."""


class NotFoundError(RdapError):
    """Represents error when requested object is not found."""


class InvalidHandleError(RdapError):
    """Requested object identifier is not valid (bad format)."""
