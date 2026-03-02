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
"""Fixtures for capturing NX output"""

import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager

import NXOpen


class CapturedOutput:
    """Wrapper for capturing data written to a temporary file."""

    def __init__(self, tmp_file: tempfile.NamedTemporaryFile):
        self._file = tmp_file
        self._out = ""

    def read(self):
        """Read the temporary file and store the contents for later access."""
        with open(self._file.name) as f:
            self._out = f.read()

    @property
    def out(self):
        """Output that was captured."""
        return self._out


@contextmanager
def capture_listing_window() -> Generator[CapturedOutput, None, None]:
    """Capture the NX listing window output. See the test for nxprint for usage."""

    # Get a temporary file to write the listing window output
    tmp_out = tempfile.NamedTemporaryFile("w", delete=False)

    # Grab the listing window and set its output to the temporary file
    listing_window = NXOpen.Session.GetSession().ListingWindow
    listing_window.SelectDevice(NXOpen.ListingWindow.DeviceType.File, str(tmp_out.name))

    captured = CapturedOutput(tmp_out)

    try:
        yield captured
    finally:
        # Close the listing window if it got left open
        if listing_window.IsOpen:
            listing_window.Close()

        # Flush the listing window's buffer by setting its output back to the window.
        # This is required in order to write to the file.
        listing_window.SelectDevice(NXOpen.ListingWindow.DeviceType.Window, "")

        # Capture the output
        captured.read()

        # Close & clean-up temporary file
        tmp_out.close()
        os.unlink(tmp_out.name)
