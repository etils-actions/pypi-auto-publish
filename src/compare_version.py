"""Compate the python version.

Outputs:

* `should-release`: Whether local_version > pypi_version ("true" or "false")
* `version`: The released `version` (to add tag)

"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import ssl
import sys
import urllib.request
from typing import Optional, Union

import packaging.version

# Any github action value
_Value = Union[str, bool]


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--module_name",
        help="Package to search.",
    )
    parser.add_argument(
        "--pkg_name",
        help="Package to search.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    module_name = args.module_name
    pkg_name = args.pkg_name

    # Add the directory containing the local module to the path
    sys.path.append(os.getcwd())

    if not pkg_name:  # pkg name and module names should match if missing
        pkg_name = module_name

    local_version = get_local_version(module_name)
    pypi_version = get_pypi_version(pkg_name)

    if pypi_version is None:  # No PyPI release yet
        pypi_version = local_version
        local_version = "0.0.0"

    local_version = packaging.version.Version(local_version)
    pypi_version = packaging.version.Version(pypi_version)
    should_release = local_version > pypi_version
    set_output("should-release", should_release)
    set_output("version", pypi_version)


# Local


def get_local_version(module_name: str) -> str:
    """Returns the local version."""
    module = importlib.import_module(module_name)
    return module.__version__


# PyPI


def get_pypi_version(pkg_name: str) -> Optional[str]:
    """Returns the last version."""
    all_versions = get_pypi_versions(pkg_name)
    if all_versions:
        return all_versions[-1]
    else:
        return None


def get_pypi_versions(pkg_name: str) -> list[str]:
    """Returns all package versions."""
    # Use PyPI API: https://warehouse.pypa.io/api-reference/json.html
    url = f"https://pypi.python.org/pypi/{pkg_name}/json"

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(url, context=ctx) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:  # Package don't exists (yet)
            return []
        else:
            raise  # Something's not right

    # Here, we could eventually filter pre-releases,... if required
    versions = list(data["releases"])
    return sorted(versions, key=packaging.version.Version)


# Github actions


def set_output(name: str, value: _Value) -> None:
    """Set github action output."""
    value = _normalize_value(value)
    return f"::set-output name={name}::{value}"


def _normalize_value(value: _Value) -> str:
    """Normalize github action output."""
    if isinstance(value, str):
        return value
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        raise TypeError(f"Invalid type {type(value)}")


if __name__ == "__main__":
    main()
