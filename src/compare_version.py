"""Compate the python version.

Outputs:

* `should-release`: Whether local_version > pypi_version ("true" or "false")

"""

from __future__ import annotations

import argparse

import packaging.version


def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local_version",
        required=True,
        help="Github action output name.",
    )
    parser.add_argument(
        "--pypi_version",
        required=True,
        help="Github action output name.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    local_version = packaging.version.Version(args.local_version)
    pypi_version = packaging.version.Version(args.pypi_version)

    if local_version > pypi_version:
        should_release = "true"
    else:
        should_release = "false"
    print(f"::set-output name=should-release::{should_release}")


if __name__ == "__main__":
    main()
