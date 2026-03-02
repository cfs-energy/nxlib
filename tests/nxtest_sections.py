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
"""Tests for nxlib.nxopen.sections module."""

import math
import unittest
from pathlib import Path

import NXOpen  # pyright: ignore[reportMissingModuleSource]

import nxlib.nxopen.section as sect
from nxlib.geometry import Plane, Point3d, Vector3d
from nxlib.nxopen.part import open_part
from tests.fixtures.common import native


@native
class TestSections(unittest.TestCase):
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

    def assertPointsAlmostEqual(
        self, point_a: Point3d, point_b: Point3d, places: int | None = None
    ):
        self.assertAlmostEqual(
            point_a.X, point_b.X, places=places, msg="X coordinates should match."
        )
        self.assertAlmostEqual(
            point_a.Y, point_b.Y, places=places, msg="Y coordinates should match."
        )
        self.assertAlmostEqual(
            point_a.Z, point_b.Z, places=places, msg="Z coordinates should match."
        )

    def test_get_section_curves(self):
        """Test that section curves can be exported."""
        section_z_coord = 10.0
        plane = Plane(Point3d(0, 0, section_z_coord), Vector3d(0, 0, 1)).to_nx(
            self.work_part
        )
        curves = sect.create_section_curves(
            self.work_part,
            plane,
            "TEST_SECTION_CURVES",
        )

        self.assertEqual(len(curves), 1, "Should only be a single body with curves")
        group_name, curve_objs = curves[0]
        self.assertEqual(group_name, "Body 1", "Group name should be as expected")

        self.assertEqual(len(curve_objs), 4, "Should be exactly four curves")

        # Make a dictionary of curves so we can make assertions about each type
        curve_dict = {curve.__class__.__name__: curve for curve in curve_objs}

        # We should have exactly one of each type of curve
        for curve_cls in ["Arc", "Ellipse", "Line", "Spline"]:
            self.assertIn(curve_cls, curve_dict.keys())

        # Test the line
        self.assertPointsAlmostEqual(
            Point3d.from_nx(curve_dict["Line"].StartPoint),
            Point3d(82.0, 111.672483056, section_z_coord),
        )
        self.assertPointsAlmostEqual(
            Point3d.from_nx(curve_dict["Line"].EndPoint),
            Point3d(82.0, 134.6156375, section_z_coord),
        )

        # Test the arc
        self.assertPointsAlmostEqual(
            Point3d.from_nx(curve_dict["Arc"].CenterPoint),
            Point3d(134.328518759, 89.589351551, section_z_coord),
        )
        self.assertEqual(curve_dict["Arc"].Radius, 100.0)
        self.assertEqual(curve_dict["Arc"].EndAngle, math.pi * 2)
        self.assertEqual(curve_dict["Arc"].StartAngle, 0.0)

        # Test the ellipse
        self.assertPointsAlmostEqual(
            Point3d.from_nx(curve_dict["Ellipse"].CenterPoint),
            Point3d(101.86068106, 111.67248306, section_z_coord),
        )

        self.assertEqual(curve_dict["Ellipse"].MajorRadius, 50.0)
        self.assertEqual(curve_dict["Ellipse"].MinorRadius, 25.0)
        self.assertAlmostEqual(
            curve_dict["Ellipse"].StartAngle, math.radians(229.11898504)
        )
        self.assertAlmostEqual(
            curve_dict["Ellipse"].EndAngle, math.radians(415.069751675)
        )
        self.assertEqual(curve_dict["Ellipse"].RotationAngle, 0.0)

        # Test the spline
        self.assertEqual(curve_dict["Spline"].Order, 4)
        self.assertEqual(curve_dict["Spline"].PoleCount, 5)

        self.assertPointsAlmostEqual(
            Point3d.from_nx(curve_dict["Spline"].Get3DPoles()[-1]),
            Point3d.from_nx(curve_dict["Line"].StartPoint),
        )

    def test_get_section_curves_empty(self):
        """Test that we don't get any curves if we don't section any geometry."""
        # No geometry intersects this plane:
        plane = Plane(Point3d(0, 0, 100), Vector3d(0, 0, 1)).to_nx(self.work_part)
        curves = sect.create_section_curves(
            self.work_part,
            plane,
            "TEST_SECTION_EMPTY_CURVES",
        )
        self.assertEqual(len(curves), 0, "Should be no curves.")

    def test_get_section_curves_name_taken(self):
        """Test that we get a ValueError if we use a name that's already taken."""
        plane = Plane(Point3d(0, 0, 100), Vector3d(0, 0, 1)).to_nx(self.work_part)
        with self.assertRaises(ValueError):
            _ = sect.create_section_curves(
                self.work_part,
                plane,
                "SECTION_CURVES",  # Name already in model
            )
