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
"""Tests for nxlib.nxopen.uf module."""

import unittest
from pathlib import Path

import NXOpen  # pyright: ignore[reportMissingModuleSource]

from nxlib.nxopen import uf
from nxlib.nxopen.part import open_part
from tests.fixtures.common import native


@native
class TestObjectTag(unittest.TestCase):
    """Test functions having to do with object tags."""

    @classmethod
    def setUpClass(cls):
        section_test_file = Path("tests") / "data" / "sections.prt"
        cls.work_part = open_part(section_test_file)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.work_part.Close(
            NXOpen.BasePart.CloseWholeTree.TrueValue,  # pyright: ignore[reportArgumentType]
            NXOpen.BasePart.CloseModified.CloseModified,  # pyright: ignore[reportArgumentType]
            None,  # pyright: ignore[reportArgumentType]
        )
        return super().tearDownClass()

    def test_get_tag_by_name(self):
        """Test that getting the tag for an existing object returns a valid tag.

        NOTE: The tag will not be the same between runs, or if the part file is
        modified. Testing the value of the returned tag is not meaningful.
        """
        existing_name = "SKETCH_000"
        found_tags = uf.get_object_tags_by_name(existing_name)
        self.assertEqual(len(found_tags), 1, "We should only find a single object")
        found_tag = found_tags.pop()
        self.assertIsInstance(found_tag, int, "Return type should be integer")
        self.assertNotEqual(
            found_tag,
            0,
            "Existing feature should not return a null tag",
        )

    def test_get_tag_by_name_multiple(self):
        """Test that we get two tags if there are two objects with the same name."""
        multiple_existing_name = "BASE"
        found_tags = uf.get_object_tags_by_name(multiple_existing_name)
        self.assertEqual(
            len(found_tags),
            2,
            f"There should be two items named '{multiple_existing_name}' in this part.",
        )
        for tag in found_tags:
            self.assertNotEqual(
                tag,
                0,
                "None of the returned tags should be the null tag.",
            )

    def test_get_tag_by_name_null(self):
        """Test that we get an empty list if we seach for something that doesn't exist."""
        found_tags = uf.get_object_tags_by_name("this_object_does_not_exist")
        self.assertEqual(
            len(found_tags),
            0,
            "Search for a non-existant object should empty list.",
        )

    def test_group_members_non_group(self):
        """Check that we get a TypeError if we pass a non-group tag."""
        nongroup_name = "SKETCH_000"
        nongroup_tag = uf.get_object_tags_by_name(nongroup_name).pop()
        with self.assertRaises(TypeError):
            _ = uf.get_group_members(nongroup_tag)

    def test_group_members_invalid_tag(self):
        """Check that we get a ValueError if we pass an invalid tag."""
        with self.assertRaises(ValueError):
            _ = uf.get_group_members(1234567)

    def test_group_members_null_tag(self):
        """Check that null tag raises ValueError."""
        with self.assertRaises(ValueError):
            _ = uf.get_group_members(0)

    def test_group_members(self):
        """Check that we can get group members."""
        group_name = "SECTION_CURVES"
        group_tag = uf.get_object_tags_by_name(group_name).pop()
        found_members = uf.get_group_members(group_tag)
        self.assertEqual(len(found_members), 4, "Should be 4 members in this group.")

        for _tag, member in found_members:
            self.assertIsInstance(
                member,
                NXOpen.TaggedObject,
                "Returned members should be TaggedObjects",
            )

    def test_group_empty(self):
        """Check that an empty group returns an empty list."""
        group_name = "EMPTY_GROUP"
        group_tag = uf.get_object_tags_by_name(group_name).pop()
        found_members = uf.get_group_members(group_tag)
        self.assertEqual(len(found_members), 0, "Group should be an empty list.")
