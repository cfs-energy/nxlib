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
import csv
import unittest
from pathlib import Path

import nxlib.nxopen.serializers.attributes as attrs
from nxlib.nxopen.part import part_context
from tests.fixtures.common import native


@native
class TestGetAttributes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assy_path = Path("tests") / "data" / "attr_assy.prt"
        cls.csvfile = Path(".") / "attrtest.csv"
        with part_context(cls.assy_path) as part:
            cls.attributes = attrs.get_assembly_attributes(
                part.ComponentAssembly.RootComponent,
                ["Material", "MassPropMass"],
                index_col="DB_PART_NO",
            )

    @classmethod
    def tearDownClass(cls):
        cls.csvfile.unlink(missing_ok=True)

    def test_attrs_serialize_roundtrip(self):
        """Test serialization of assembly attributes."""
        outfile = attrs.write_assembly_attributes(
            self.attributes,
            outfile=self.csvfile,
            index_col="DB_PART_NO",
        )

        self.assertEqual(outfile, self.csvfile)
        attributes = {}
        with open(self.csvfile) as metadata_file:
            reader = csv.DictReader(metadata_file)
            for row in reader:
                row_index = row.pop("DB_PART_NO")
                attributes[row_index] = row

        self.assertEqual(
            attributes["attr_assy"]["MassPropMass"],
            "",
            msg="Top level assembly should not have mass.",
        )
        self.assertEqual(
            attributes["attr_assy"]["Material"],
            "",
            msg="Top level assembly should not have a material.",
        )
        self.assertTrue(
            isinstance(attributes["model1"]["MassPropMass"], str),
            msg="Detail component should have mass.",
        )
        self.assertTrue(
            isinstance(attributes["model1"]["Material"], str),
            msg="Detail component should have material",
        )

    def test_get_attributes(self):
        """Test recursive export of part attributes."""

        for model_name in ["model1", "model2", "attr_assy"]:
            assert model_name in self.attributes.keys()

        self.assertIsNone(
            self.attributes["attr_assy"]["MassPropMass"],
            msg="Top level assembly should not have mass.",
        )
        self.assertIsNone(
            self.attributes["attr_assy"]["Material"],
            msg="Top level assembly should not have a material.",
        )
        self.assertTrue(
            isinstance(self.attributes["model1"]["MassPropMass"], str),
            msg="Detail component should have mass.",
        )
        self.assertTrue(
            isinstance(self.attributes["model1"]["Material"], str),
            msg="Detail component should have material",
        )
