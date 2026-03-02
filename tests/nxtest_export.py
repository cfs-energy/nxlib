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
"""Tests for nxlib.nxopen.export module."""

import unittest
from pathlib import Path

from nxlib.nxopen.export import export_expressions
from nxlib.nxopen.part import part_context
from tests.fixtures.common import native


class ExportExpressionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file = Path(".") / "something.exp"

    @classmethod
    def tearDownClass(cls):
        cls.file.unlink(missing_ok=True)

    @native
    def test_export(self):
        """Test that expressions for a part file can be exported,
        and that an expected expression is in the result."""
        with (
            part_context("tests/data/model1.prt") as model,
        ):
            export_expressions(model, self.file)

        with open(self.file, "r") as output:
            # Expect expression p1=25 to be in model1.prt
            self.assertRegex(output.read(), "p1=25")
