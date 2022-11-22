"""Compate the python version.

Outputs:

* `should-release`: Whether local_version > pypi_version ("true" or "false")
* `version`: The released `version` (to add tag)

"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import ssl
import sys
import urllib.request
from typing import Union

import packaging.version

# Any github action value
_Value = Union[str, bool]


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pkg_name",
        help="Package to search.",
    )
    return parser.parse_args()


def main():
    # Add the directory containing the local module to the path
    sys.path.append(os.getcwd())

    args = parse_arguments()
    pkg_name = args.pkg_name

    if not pkg_name:  # pkg name and module names should match if missing
        pkg_name = find_pkg_name()

    local_version = get_local_version(pkg_name)
    pypi_version = get_pypi_version(pkg_name)

    set_output("version", local_version)

    local_version = packaging.version.Version(local_version)
    pypi_version = packaging.version.Version(pypi_version)
    set_output("should-release", local_version > pypi_version)


# Local


def _is_editable(dist: importlib.metadata.PathDistribution) -> bool:
    all_pth = [f for f in dist.files if f.name.endswith(".pth")]
    if len(all_pth) != 1:  # Might be edge case if >1, unsure if possible
        return False
    (pth_file,) = all_pth
    content = pth_file.read_text()
    if content.startswith("/"):  # TODO: To delete
        print(content)
    # Here, should check with github action path
    return content.startswith("/")


def find_pkg_name() -> str:
    dists = [dist for dist in importlib.metadata.distributions() if _is_editable(dist)]
    if len(dists) != 1:
        names = [d.name for d in dists]
        raise ValueError(
            f"Could not auto-infer the package name: {names}. Please open an issue."
        )
    (dist,) = dists
    return dist.name


def get_local_version(pkg_name: str) -> str:
    """Returns the local version."""
    return importlib.metadata.version(pkg_name)


# PyPI


def get_pypi_version(pkg_name: str) -> str:
    """Returns the last version."""
    all_versions = get_pypi_versions(pkg_name)
    if all_versions:
        return all_versions[-1]
    else:  # No PyPI release yet
        return "0.0.0"


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

    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        print(f'{name}={value}', file=f)


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
