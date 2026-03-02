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
"""Run unit tests on NX functions."""

import argparse
import sys
from pathlib import Path

import nxlib
from nxlib.tc_auth import TcAuthMethod
from nxlib.utility.common import add_runmode_group

from . import TEST_DISCOVERY_PATTERN


class ActionPytestRunner(argparse.Action):
    """Shortcut for `--local --runner=pytest`"""

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, "runner", "pytest")
        setattr(namespace, "local", True)


def parser() -> argparse.ArgumentParser:
    """ArgumentParser importable by NX. This allows for cleanly passing
    arguments from the CLI to the NX-based test runner."""
    parser = argparse.ArgumentParser(
        prog="nxlib",
        description="Test runner for nxlib. This test runner looks in files that"
        + f" match the pattern '{TEST_DISCOVERY_PATTERN}'.",
        epilog="See `python -m unittest --help` or `pytest --help` for additional"
        + " command line options.",
    )
    parser.add_argument(
        "--runner",
        type=str,
        choices=["unittest", "pytest"],
        default="unittest",
        help="Test runner to use, default is unittest (built-in).",
    )
    parser.add_argument(
        "-p",
        "--pytest",
        nargs=0,
        action=ActionPytestRunner,
        help="Use pytest as the test runner, and use the local environment."
        + " Equivalent to `--local --runner=pytest`.",
    )
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        default=False,
        help="Use the local Python interpreter rather than the NX built-in Python.",
    )
    add_runmode_group(parser)
    parser.add_argument(
        "--auth",
        type=TcAuthMethod,
        default="auto",
        help="Authentication method for Teamcenter. Choose from 'auto' (default), 'sso' or 'password'.",
    )
    parser.add_argument(
        "--allow-extern-nxlib",
        default=False,
        action="store_true",
        help="Allow tests to run with a symlinked version of nxlib that is different "
        + "than the one being used to invoke the test suite.",
    )
    return parser


def main():
    """Main entry point for nxlib test runner (nxtest)."""
    args, _ = parser().parse_known_args()
    if not (nxlib.status.nxlib_symlinked or args.allow_extern_nxlib):
        print(
            "ERROR: The version of nxlib that is symlinked to NX is not the ",
            "same version that is being used to run these tests!\n",
            "Please run `nxlib install --overwrite` or call the test suite with the ",
            "--allow-extern-nxlib flag to continue.",
        )
        exit(1)
    exit(
        nxlib.run_journal(
            Path(__file__).resolve().parent / "_nx_run_test.py",
            sys.argv[1:],
            run_mode=args.run_mode,
            local=args.local,
            auth_method=args.auth,
        )
    )


if __name__ == "__main__":
    main()
