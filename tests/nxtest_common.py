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
"""Tests for nxlib.nxopen.teamcenter module."""

import tempfile
import unittest

from nxlib import nxprint
from tests.fixtures.capture import capture_listing_window


class TestPrintFunction(unittest.TestCase):
    def test_nxprint(self):
        """Test that standard output can be captured."""

        test_str = "Hello World!"
        with capture_listing_window() as captured:
            nxprint(test_str)
        self.assertEqual(test_str, captured.out.strip())

    def test_nxprint_file(self):
        """Test that nxprint can print to a file."""
        test_str = "Hello World!"
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            nxprint(test_str, file=tmp.name)
            with open(tmp.name) as output:
                captured = output.read()
        self.assertEqual(test_str, captured.strip())
