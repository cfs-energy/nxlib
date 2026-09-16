# Copyright 2026 Commonwealth Fusion Systems (CFS), all rights reserved.
# This entire source code file represents the sole intellectual property of CFS.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command line tools and utilities for nxlib."""

import argparse
import logging
import sys
from pathlib import Path

import nxlib
from nxlib.tc_auth import TcAuthMethod
from nxlib.utility.common import add_runmode_group

from . import install

logger = logging.getLogger(__name__)


def main() -> None:
    """Command line entry point for nxlib utilities."""
    logging.basicConfig(
        format="[%(levelname)s] [%(name)s]: %(message)s", level=logging.INFO
    )
    parser = argparse.ArgumentParser(
        description=f"Command line utilities for nxlib. Version {nxlib.__version__}"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the version and exit.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        type=str.upper,
        help="Set the logging level",
    )
    subparsers = parser.add_subparsers(title="Commands", metavar="", dest="command")

    # Install
    inst_parser = subparsers.add_parser(
        "install",
        help="Make nxlib available to your local NX installation.",
        description="Make nxlib available for import by all nx journals by"
        " creating a directory symbolic link from the NX Python path to nxlib.",
    )
    inst_parser.add_argument(
        "-y",
        "--overwrite",
        action="store_true",
        help="Overwrite the existing installation.",
    )

    # Uninstall
    subparsers.add_parser(
        "remove", help="Remove nxlib from your local NX installation."
    )

    # Status
    status_parser = subparsers.add_parser(
        "status", help="Show nxlib installation status."
    )
    status_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed nxlib status."
    )

    # Typings
    typings_parser = subparsers.add_parser(
        "typings", help="Install NXOpen type stubs to your development environment."
    )
    typings_parser.add_argument(
        "--project-root",
        "-p",
        type=Path,
        default=Path("typings"),
        help="Development root to which typings should be installed.",
    )
    typings_parser.add_argument(
        "-y",
        "--overwrite",
        action="store_true",
        help="Overwrite existing typings.",
    )
    typings_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the files that would be copied, but don't copy anything.",
    )

    # Run
    run_parser = subparsers.add_parser(
        "run",
        help="Run a journal or arbitrary Python code with NX.",
        description="Run a journal or arbitrary Python code with NX.",
    )
    journal_group = run_parser.add_mutually_exclusive_group(required=True)
    journal_group.add_argument(
        "journal_path",
        nargs="?",
        default=None,
        type=Path,
        help="Path to journal to run.",
    )
    journal_group.add_argument(
        "-c",
        "--code",
        type=str,
        help="Execute arbitrary Python code with the NX interpreter.",
    )

    add_runmode_group(run_parser)

    run_parser.add_argument(
        "--local",
        action="store_true",
        help="Use the local Python interpreter rather than the NX built-in Python.",
    )
    run_parser.add_argument(
        "--auth",
        type=TcAuthMethod,
        default="auto",
        help="Authentication method for Teamcenter. Choose from 'auto' (default), 'sso'"
        " or 'password'.",
    )

    args, remainder = parser.parse_known_args()
    logger.setLevel(args.log_level)

    if args.version:
        print(f"nxlib version {nxlib.__version__}")
        return

    match args.command:
        case "install":
            try:
                sys.exit(install.install_to_nx(overwrite=args.overwrite))
            except FileExistsError as err:
                logger.error("%s\nTry rerunning with --overwrite", err)
                sys.exit(1)
            except nxlib.NxNotInstalledError as err:
                logger.error("%s", err)
                sys.exit(2)
        case "run":
            remainder = [arg for arg in remainder if arg != "--"]
            run_journal_kwargs = {
                "run_mode": args.run_mode,
                "auth_method": args.auth,
                "local": args.local,
                "log_level": args.log_level,
            }
            if args.code:
                sys.exit(nxlib.run_python(args.code, *remainder, **run_journal_kwargs))
            else:
                sys.exit(
                    nxlib.run_journal(
                        args.journal_path, *remainder, **run_journal_kwargs
                    )
                )
        case "status":
            if args.verbose:
                print(nxlib.status)
            else:
                install.show_install_status()
        case "remove":
            try:
                sys.exit(install.uninstall_from_nx())
            except (nxlib.NxNotInstalledError, FileNotFoundError) as err:
                logger.error("%s", err)
                sys.exit(1)
        case "typings":
            try:
                sys.exit(
                    install.install_typings(
                        development_base=args.project_root,
                        overwrite=args.overwrite,
                        dry_run=args.dry_run,
                    )
                )
            except FileExistsError as err:
                logger.error("%s\nTry rerunning with --overwrite", err)
                sys.exit(1)
            except PermissionError as err:
                logger.error(
                    "Error with file permissions: %s\nTry manually removing your "
                    "typings directory first.",
                    err,
                )
                sys.exit(2)
            except nxlib.NxNotInstalledError as err:
                logger.error("%s", err)
                sys.exit(3)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
