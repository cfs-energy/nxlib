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
from pathlib import Path

import nxlib
from nxlib.tc_auth import TcAuthMethod
from nxlib.utility.common import add_runmode_group

from . import install


def main() -> None:
    """Command line entry point for nxlib utilities."""
    parser = argparse.ArgumentParser(
        description="Command line utilities for nxlib. Version %s." % nxlib.__version__
    )
    parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="Print the version and exit.",
    )
    subparsers = parser.add_subparsers(title="Commands", metavar="", dest="command")

    # Install
    inst_parser = subparsers.add_parser(
        "install",
        help="Make nxlib available to your local NX installation.",
        description="""Make nxlib available for import by all nx journals by
        creating a directory symbolic link from the NX Python path to nxlib.""",
    )
    inst_parser.add_argument(
        "-y", "--overwrite", action="store_true", default=False, required=False
    )

    # Uninstall
    subparsers.add_parser(
        "remove", help="Remove nxlib from your local NX installation."
    )

    # Status
    status_parser = subparsers.add_parser(
        "status", help="Show nxlib installation status"
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
        default=False,
        help="Overwrite existing typings.",
    )
    typings_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show the files that would be copied, but don't copy anything.",
    )

    # Run
    run_parser = subparsers.add_parser(
        "run",
        help="Run a journal or arbitrary Python code with NX",
        description="Run a journal or arbitrary Python code with NX.",
    )
    journal_group = run_parser.add_mutually_exclusive_group(required=True)
    journal_group.add_argument(
        "journal_path",
        nargs="?",
        default=None,
        type=Path,
        help="Path to journal to run",
    )
    journal_group.add_argument(
        "-c",
        "--code",
        type=str,
        help="Execute arbitrary Python code with the NX interpreter.",
    )
    run_parser.add_argument(
        "--args",
        nargs="*",
        help="Arguments to pass to the journal",
    )

    add_runmode_group(run_parser)

    run_parser.add_argument(
        "--local",
        action="store_true",
        default=False,
        help="Use the local Python interpreter rather than the NX built-in Python.",
    )
    run_parser.add_argument(
        "--auth",
        type=TcAuthMethod,
        default="auto",
        help="Authentication method for Teamcenter. Choose from 'auto' (default), 'sso' or 'password'.",
    )
    run_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed nxlib status."
    )

    args = parser.parse_args()
    if args.version:
        print("nxlib version %s" % nxlib.__version__)
        return

    match args.command:
        case "install":
            try:
                exit(install.install_to_nx(overwrite=args.overwrite))
            except FileExistsError as err:
                print("ERROR: %s" % err)
                print("Try rerunning with --overwrite.")
                exit(1)
            except (nxlib.NxNotInstalledError, FileExistsError) as err:
                print("ERROR: %s" % err)
                exit(2)
        case "run":
            run_journal_kwargs = dict(
                journal_args=args.args,
                run_mode=args.run_mode,
                auth_method=args.auth,
                local=args.local,
                verbose=args.verbose,
            )
            if args.code:
                exit(nxlib.run_python(args.code, **run_journal_kwargs))
            else:
                exit(nxlib.run_journal(args.journal_path, **run_journal_kwargs))
        case "status":
            if args.verbose:
                print(nxlib.status)
            else:
                install.show_install_status()
        case "remove":
            try:
                exit(install.uninstall_from_nx())
            except (nxlib.NxNotInstalledError, FileNotFoundError) as err:
                print("ERROR: %s" % err)
                exit(1)
        case "typings":
            try:
                exit(
                    install.install_typings(
                        development_base=args.project_root,
                        overwrite=args.overwrite,
                        dry_run=args.dry_run,
                    )
                )
            except FileExistsError as err:
                print("ERROR: %s" % err)
                print("Try rerunning with --overwrite.")
                exit(1)
            except PermissionError:
                print(
                    "Error with file permissions, try manually removing your typings directory first."
                )
                exit(2)
            except nxlib.NxNotInstalledError as err:
                print("ERROR: %s" % err)
                exit(3)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
