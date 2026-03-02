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
"""NXOpen journal to run test cases with the NX interpreter."""

import sys
import unittest

from nxlib.nxtest import TEST_DISCOVERY_PATTERN  # noqa: I001
from nxlib.nxtest.main import parser  # noqa: I001


def _test_with_unittest(unittest_args) -> int:
    """Execute unittest, and return code 0 if tests pass, 1 otherwise."""
    args = ["unittest", "discover", "--pattern", TEST_DISCOVERY_PATTERN] + unittest_args
    test_prog = unittest.main(module=None, argv=args, exit=False)
    result = test_prog.result
    return int(not result.wasSuccessful())


def _test_with_pytest(pytest_args) -> int:
    """Execute pytest, and return code 0 if tests pass, 1 otherwise."""
    # importing pytest is done here, since pytest is not required by default
    # for nxlib tests. If this function is called, it's assumed that the
    # user has pytest installed and is running NX with their local Python environment.
    # This import will fail very quickly if NX cannot see pytest.
    import pytest  # noqa: I001

    pytest_args = [
        # Override the typical file search pattern ("test*.py") with
        # a custom search pattern for nxlib
        "--override-ini",
        "python_files=%s" % TEST_DISCOVERY_PATTERN,
    ] + pytest_args
    return int(pytest.main(pytest_args))


def main():
    """Entry point for test runner journal."""
    args, runner_args = parser().parse_known_args()
    match args.runner:
        case "pytest":
            return _test_with_pytest(runner_args)
        case "unittest":
            return _test_with_unittest(runner_args)
        case _:
            raise ValueError("Invalid runner: %s" % args.runner)


if __name__ == "__main__":
    result = main()
    # Calling `sys.exit(0)` from within an NX journal will raise an exception,
    # causing the exit code for run_journal.exe to be 1, even if the test suite
    # passed. Thus we only call sys.exit if the test suite failed, otherwise
    # we let the journal run its course, return an exit code of 0 for run_journal.exe
    if result != 0:
        sys.exit(result)
