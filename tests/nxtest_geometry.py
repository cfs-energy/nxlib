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
"""Tests for nxlib.geometry, including converstion to and from NXOpen objects."""

import random
import unittest
from math import pi
from pathlib import Path
from typing import Any, Type

import NXOpen  # pyright: ignore[reportMissingModuleSource]

from nxlib import geometry
from nxlib.geometry import Geometry
from nxlib.nxopen.part import open_part
from tests.fixtures.common import (
    native,
    rand_coords,
    rand_norm_vec,
    rand_orthonormal_mat3,
)


@native
class TestPlaneGeometry(unittest.TestCase):
    """Test creation & serialization of plane geometry from a datum plane
    feature within a part."""

    @classmethod
    def setUpClass(cls):
        file = Path("tests") / "data" / "planetest.prt"
        part = open_part(file)
        cls.feature = [
            feat
            for feat in part.Features  # pyright: ignore[reportGeneralTypeIssues]
            if feat.Name == "TEST_PLANE"
        ].pop()
        cls.plane: NXOpen.Plane = part.Planes.CreatePlane(cls.feature)

    def test_plane_geom_origin(self):
        """Test that the origin of a serialized plane matches the input."""
        serialized_plane = Geometry.from_nx(self.plane)
        self.assertEqual(
            serialized_plane.origin.X, self.plane.Origin.X, "X coordinates should match"
        )
        self.assertEqual(
            serialized_plane.origin.Y, self.plane.Origin.Y, "Y coordinates should match"
        )
        self.assertEqual(
            serialized_plane.origin.Z, self.plane.Origin.Z, "Z coordinates should match"
        )

    def test_plane_creation(self):
        """Test that plane is created with make_geometry function, and that
        normal an origin of plane are expected values."""
        serialized_plane = Geometry.from_nx(self.plane)
        self.assertEqual(
            serialized_plane.origin, geometry.Point3d(8, 9, 10), "origin should match"
        )
        self.assertAlmostEqual(
            serialized_plane.normal.X, 0.707, 3, "normal X should match"
        )
        self.assertAlmostEqual(
            serialized_plane.normal.Y, 0.707, 3, "normal Y should match"
        )
        self.assertAlmostEqual(
            serialized_plane.normal.Z, 0.0, 3, "normal Z should match"
        )

    def test_plane_geom_normal(self):
        """Test that the normal of a serialized plane matches the input."""
        serialized_plane = Geometry.from_nx(self.plane)
        self.assertEqual(
            serialized_plane.normal.X, self.plane.Normal.X, "X coordinates should match"
        )
        self.assertEqual(
            serialized_plane.normal.Y, self.plane.Normal.Y, "Y coordinates should match"
        )
        self.assertEqual(
            serialized_plane.normal.Z, self.plane.Normal.Z, "Z coordinates should match"
        )


@native
class TestGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        section_test_file = Path("tests") / "data" / "planetest.prt"
        cls.work_part = open_part(section_test_file)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.work_part.Close(
            NXOpen.BasePart.CloseWholeTree.TrueValue,  # pyright: ignore[reportArgumentType]
            NXOpen.BasePart.CloseModified.CloseModified,  # pyright: ignore[reportArgumentType]
            None,  # pyright: ignore[reportArgumentType]
        )
        return super().tearDownClass()

    def test_point_3d(self):
        """Test Point3D creation."""
        coords = rand_coords(3)
        pt = geometry.Point3d(*coords).to_nx()
        self.assertIsInstance(pt, NXOpen.Point3d)

    def test_point_3d_ints(self):
        """Test that we can make a Point3d if we supply integer coordinates."""
        coords = [int(c) for c in rand_coords(3)]
        pt = geometry.Point3d(*coords).to_nx()
        self.assertIsInstance(pt, NXOpen.Point3d)

    def test_vec_3d(self):
        """Test Vector3d creation."""
        coords = rand_coords(3)
        pt = geometry.Vector3d(*coords).to_nx()
        self.assertIsInstance(pt, NXOpen.Vector3d)

    def test_vec_3d_ints(self):
        """Test that we can make a Vector3d if we supply integer coordinates."""
        coords = [int(c) for c in rand_coords(3)]
        pt = geometry.Vector3d(*coords).to_nx()
        self.assertIsInstance(pt, NXOpen.Vector3d)

    def test_plane_coords(self):
        """Test that we can create a plane with coordinates."""
        origin = geometry.Point3d(*rand_coords(3))
        normal = geometry.Vector3d(*rand_norm_vec())
        plane = geometry.Plane(origin, normal).to_nx(self.work_part)
        self.assertIsInstance(plane, NXOpen.Plane, "Output should be a plane class")
        self.assertAlmostEqual(
            origin[0],
            plane.Origin.X,
            msg="X-coordinate should match",
        )
        self.assertAlmostEqual(
            origin[1],
            plane.Origin.Y,
            msg="Y-coordinate should match",
        )
        self.assertAlmostEqual(
            origin[2],
            plane.Origin.Z,
            msg="Z-coordinate should match",
        )

        self.assertAlmostEqual(
            normal[0],
            plane.Normal.X,
            msg="X value of normal should match",
        )
        self.assertAlmostEqual(
            normal[1],
            plane.Normal.Y,
            msg="Y value of normal should match",
        )
        self.assertAlmostEqual(
            normal[2],
            plane.Normal.Z,
            msg="Z value of normal should match",
        )


@native
class TestRoundtripGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        section_test_file = Path("tests") / "data" / "planetest.prt"
        cls.work_part = open_part(section_test_file)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.work_part.Close(
            NXOpen.BasePart.CloseWholeTree.TrueValue,  # pyright: ignore[reportArgumentType]
            NXOpen.BasePart.CloseModified.CloseModified,  # pyright: ignore[reportArgumentType]
            None,  # pyright: ignore[reportArgumentType]
        )
        return super().tearDownClass()

    def _test_coordseq_roundtrip(
        self,
        n: int,
        nxopen_cls: Type,
        nxlib_cls: Type[geometry.Geometry],
        attrs: list[str],
    ):
        origin = rand_coords(n)
        point = nxopen_cls(*origin)
        point_model = Geometry.from_nx(point)
        self.assertIsInstance(point_model, nxlib_cls)
        point_ser = point_model.to_json()
        point_deser = Geometry.from_json(point_ser)
        self.assertIsInstance(point_model, nxlib_cls)
        point_roundtrip = point_deser.to_nx()

        for attr in attrs:
            original_coord = getattr(point, attr)
            roundtrip_coord = getattr(point_roundtrip, attr)
            self.assertIsNotNone(original_coord)
            self.assertIsNotNone(roundtrip_coord)
            self.assertEqual(
                original_coord,
                roundtrip_coord,
                f"{attr}-coordinates should match exactly.",
            )

    def test_point3d_roundtrip(self):
        self._test_coordseq_roundtrip(
            3, NXOpen.Point3d, geometry.Point3d, ["X", "Y", "Z"]
        )

    def test_vector3d_roundtrip(self):
        self._test_coordseq_roundtrip(
            3, NXOpen.Vector3d, geometry.Vector3d, ["X", "Y", "Z"]
        )

    def test_point4d_roundtrip(self):
        self._test_coordseq_roundtrip(
            4, NXOpen.Point4d, geometry.Point4d, ["X", "Y", "Z", "W"]
        )

    def test_matrix3x3_roundtrip(self):
        self._test_coordseq_roundtrip(
            9,
            NXOpen.Matrix3x3,
            geometry.Matrix3x3,
            ["Xx", "Xy", "Xz", "Yx", "Yy", "Yz", "Zx", "Zy", "Zz"],
        )

    def _test_geometry_roundtrip(
        self, geo_cls: Type[geometry.Geometry], nx_class: Type, attrs: dict[str, Any]
    ):
        # Create an NXOpen object
        original = geo_cls(**attrs).to_nx(self.work_part)
        self.assertIsInstance(original, nx_class)

        # Create a model of it from nx
        model = Geometry.from_nx(original)
        self.assertIsInstance(model, geo_cls)

        # Serialize to JSON and deserialize
        model_serialized = model.to_json()
        model_deserialized = Geometry.from_json(model_serialized)

        # Make sure it's still the right class
        self.assertIsInstance(model_deserialized, geo_cls)

        # Test that the attributes match
        for attr in attrs.keys():
            self.assertEqual(
                getattr(model, attr),
                getattr(model_deserialized, attr),
                f"{attr} should match.",
            )

    def test_line_roundtrip(self):
        self._test_geometry_roundtrip(
            geometry.Line, NXOpen.Line, {"start": rand_coords(3), "end": rand_coords(3)}
        )

    def test_plane_roundtrip(self):
        self._test_geometry_roundtrip(
            geometry.Plane,
            NXOpen.Plane,
            {"origin": rand_coords(3), "normal": rand_norm_vec()},
        )

    def test_arc_roundtrip(self):
        self._test_geometry_roundtrip(
            geometry.Arc,
            NXOpen.Arc,
            {
                "radius": random.random() * 1000,
                "start_angle": random.random() * 2 * pi,
                "end_angle": random.random() * 2 * pi,
                "center": rand_coords(3),
                "matrix": rand_orthonormal_mat3(),
            },
        )

    def test_ellipse_roundtrip(self):
        self._test_geometry_roundtrip(
            geometry.Ellipse,
            NXOpen.Ellipse,
            {
                "major_radius": random.random() * 1000,
                "minor_radius": random.random() * 1000,
                "start_angle": random.random() * 2 * pi,
                "end_angle": random.random() * 2 * pi,
                "rot_angle": random.random() * 2 * pi,
                "center": rand_coords(3),
                "matrix": rand_orthonormal_mat3(),
            },
        )

    def test_spline_roundtrip(self):
        with self.assertRaises(NotImplementedError):
            self._test_geometry_roundtrip(
                geometry.Spline,
                NXOpen.Spline,
                {
                    "order": 2,
                    "knots": [0, 0, 1, 0],
                    "poles": [
                        geometry.Point4d(*rand_coords(4)),
                        geometry.Point4d(*rand_coords(4)),
                    ],
                },
            )
