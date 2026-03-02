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
"""Common command-line and utility functions."""

import argparse
from typing import Literal, get_args

RunMode = Literal["native", "managed"]


def add_runmode_group(parser: argparse.ArgumentParser) -> None:
    """Add the ``--run-mode`` option to an an ``argparse.ArgumentParser``.

    Parameters
    ----------
    parser
        The parser to add the ``--run-mode`` option to.
    """
    runmode_group = parser.add_mutually_exclusive_group(required=False)
    runmode_group.add_argument(
        "--run-mode",
        choices=get_args(RunMode),
        default="native",
        help="NX run mode. 'native' (default) for local filesystem and 'managed' for Teamcenter.",
    )
    runmode_group.add_argument(
        "--native",
        action="store_const",
        const="native",
        dest="run_mode",
        help="Run with NX native (local filesystem)",
    )
    runmode_group.add_argument(
        "--managed",
        "--teamcenter",
        action="store_const",
        const="managed",
        dest="run_mode",
        help="Run with managed (Teamcenter) NX",
    )
