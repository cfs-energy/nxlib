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
"""Build the nxlib documentation using pdoc."""

import argparse
import os
from pathlib import Path
from unittest.mock import Mock

import pdoc


class NxOpenMock(Mock):
    """Mock class to represent the NXOpen package.

    We can't import NXOpen, so pdoc will fail if we leave this alone. Using
    the ``unittest.Mock`` class allows us to use any number of submodule levels
    of NXOpen imports in our code, (e.g. import NXOpen.Something.Completely.Different)
    while letting it show up correctly in the documentation.
    """

    @classmethod
    def __or__(cls, _other):
        """We mock the __or__ and __ror__ magic methods so that type hinting works out.
        Without this we get ``TypeError: Unsupporeted operand types for |: 'Mock' and 'Mock'``
        """
        return cls

    @classmethod
    def __ror__(cls, _other):
        return cls

    def __repr__(self):
        """The repr is used in the docstrings. This gives correct-looking type hints
        on the functions that take or return NXOpen objects."""
        return self._extract_mock_name()


def _mock_import(name, globals=[], locals={}, fromlist=[], level=0):
    """Import function that returns NxOpenMock rather than failing on
    ``import NXOpen``"""
    try:
        return _real_import(name, globals, locals, fromlist, level)
    except ImportError as err:
        if "NXOpen" in err.msg:
            return NxOpenMock(name="NXOpen")
        # If there was a genuine non-NXOpen error in the library, raise it
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "generate docs", description="Generate the nxlib documentation."
    )
    parser.add_argument(
        "build_dir", type=Path, help="Output directory for documentation build."
    )
    parser.add_argument(
        "--format",
        choices=["html", "markdown"],
        default="html",
        help="Output format (default: html).",
    )
    args = parser.parse_args()
    # Replace the import function with the mock function above. This allows
    # a workaround when pdoc tries to import NXOpen.
    _real_import, __builtins__.__import__ = __builtins__.__import__, _mock_import

    # Set this special environment variable, which tells nxlib that it can import
    # both NXOpen functions as if it were running NX, and utility functions as if
    # it were running from a local Python environment. This causes
    # nxlib.status.nx_execution_mode to be set to a special "_DOCGEN" status.
    os.environ["NXLIB_DOCGEN"] = ""

    # Set rendering uptions
    pdoc.render.configure(docformat="numpy")  # pyright: ignore[reportPrivateImportUsage]

    # Build the documentation
    doc = pdoc.pdoc("nxlib", output_directory=args.build_dir, format=args.format)
