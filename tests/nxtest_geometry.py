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

    def test_csys_roundtrip(self):
        self._test_geometry_roundtrip(
            geometry.CartesianCoordinateSystem,
            NXOpen.CartesianCoordinateSystem,
            {
                "origin": rand_coords(3),
                "orientation": rand_orthonormal_mat3(),
            },
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


@native
class TestTransformGeometry(unittest.TestCase):
    """Test the ``Geometry.transform`` function."""

    @classmethod
    def setUpClass(cls):
        # The transformed feature assembly has a single component
        # called transformed_feature. This component is a part file with several
        # features that are defined relative to the the component origin
        # Note that all features are in the "MODEL" reference set which avoids
        # this test needing to switch to "Entire Part" to test datums, etc.
        transform_test_assy = Path("tests") / "data" / "transformed_feature_assy.prt"
        cls.work_part = open_part(transform_test_assy, open_assembly=True)
        root_component = cls.work_part.ComponentAssembly.RootComponent

        # Find the component with features we're going to want to query
        cls.feature_component = root_component.GetChildren()[0]

        # The position of the component is a tuple of Point3d, Matrix3x3
        cls.transform = cls.feature_component.GetPosition()

        cls.feature_part = cls.feature_component.Prototype
        cls.feature_part.LoadFully()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.work_part.Close(
            NXOpen.BasePart.CloseWholeTree.TrueValue,  # pyright: ignore[reportArgumentType]
            NXOpen.BasePart.CloseModified.CloseModified,  # pyright: ignore[reportArgumentType]
            None,  # pyright: ignore[reportArgumentType]
        )
        return super().tearDownClass()

    def _get_feature(self, feature_name: str) -> NXOpen.NXObject:
        """Get a uniquely-named feature from the feature part."""
        feats = [f for f in self.feature_part.Features if f.Name == feature_name]
        self.assertEqual(len(feats), 1, "Feature should have been found in test part")
        return feats.pop()

    def test_transform_point3d(self):
        """Test Point3d transformation"""
        point_feat: NXOpen.Features.PointFeature = self._get_feature("OFFSET_PT")
        point_entity: NXOpen.Point = point_feat.GetEntities().pop()
        coords: NXOpen.Point3d = point_entity.Coordinates

        # Transform the point using the function under test
        transformed_point = Geometry.from_nx(coords).transform(*self.transform)

        # Now measure the feature relative to the top level of the assembly:
        point_occurrence = self.feature_component.FindOccurrence(point_entity)

        point_occ_geometry = Geometry.from_nx(point_occurrence.Coordinates)

        self.assertEqual(
            transformed_point,
            point_occ_geometry,
            "Transformation should match feature occurrence within assembly.",
        )

    def test_transform_line(self):
        """Test line transformation."""
        line_feat: NXOpen.Features.AssociativeLine = self._get_feature("OFFSET_LINE")
        line_entity: NXOpen.Line = line_feat.GetEntities().pop()

        transformed_line = Geometry.from_nx(line_entity).transform(*self.transform)
        line_occurrence: NXOpen.Line = self.feature_component.FindOccurrence(
            line_entity
        )  # pyright: ignore[reportAssignmentType]

        line_occ_geometry = Geometry.from_nx(line_occurrence)

        self.assertEqual(
            transformed_line.start, line_occ_geometry.start, "Start points should match"
        )
        self.assertEqual(
            transformed_line.end, line_occ_geometry.end, "End points should match"
        )

    def test_transform_arc(self):
        """Test arc transformation."""
        arc_feat: NXOpen.Features.AssociativeArc = self._get_feature("OFFSET_ARC")
        arc_entity: NXOpen.Arc = arc_feat.GetEntities().pop()

        transformed_arc = Geometry.from_nx(arc_entity).transform(*self.transform)

        arc_occurrence: NXOpen.Arc = self.feature_component.FindOccurrence(arc_entity)  # pyright: ignore[reportAssignmentType]

        arc_occ_geom = Geometry.from_nx(arc_occurrence)

        for attr in ["radius", "start_angle", "end_angle", "center"]:
            self.assertEqual(
                getattr(transformed_arc, attr),
                getattr(arc_occ_geom, attr),
                f"{attr} should match",
            )

        self._assert_mat3_almost_equal(transformed_arc.matrix, arc_occ_geom.matrix)

    def test_transform_not_implemented(self):
        """Test spline transformation (not implemented)."""
        # TODO (SW-17276): Add test case for spline transformation
        spline_feat: NXOpen.Features.StudioSpline = self._get_feature("OFFSET_SPLINE")
        spline_entity: NXOpen.Spline = spline_feat.GetEntities().pop()

        with self.assertRaises(NotImplementedError):
            _ = Geometry.from_nx(spline_entity).transform(*self.transform)

    def test_transform_plane(self):
        """Test plane transformation."""
        plane_feat: NXOpen.Features.DatumPlaneFeature = self._get_feature(
            "OFFSET_PLANE"
        )
        plane_entity: NXOpen.DatumPlane = plane_feat.GetEntities().pop()

        transformed_plane = Geometry.from_nx(plane_entity).transform(*self.transform)

        plane_occurrence: NXOpen.DatumPlane = self.feature_component.FindOccurrence(
            plane_entity
        )  # pyright: ignore[reportAssignmentType]

        plane_occ_geom = Geometry.from_nx(plane_occurrence)

        for attr in ["origin", "normal"]:
            self.assertEqual(
                getattr(transformed_plane, attr),
                getattr(plane_occ_geom, attr),
                f"{attr} should match",
            )

    def test_transform_csys(self):
        """Test Coordinate System transformation"""
        csys_feat: NXOpen.Features.DatumCsys = self._get_feature("OFFSET_CSYS")
        csys_entity: NXOpen.CartesianCoordinateSystem = [
            ent
            for ent in csys_feat.GetEntities()
            if isinstance(ent, NXOpen.CartesianCoordinateSystem)
        ].pop()

        # Transform the point using the function under test
        transformed_csys = Geometry.from_nx(csys_entity).transform(*self.transform)

        # Now measure the feature relative to the top level of the assembly:
        csys_occurrence: NXOpen.CartesianCoordinateSystem = (
            self.feature_component.FindOccurrence(csys_entity)
        )  # pyright: ignore[reportAssignmentType]

        csys_occ_geometry = Geometry.from_nx(csys_occurrence)

        self.assertEqual(
            transformed_csys.origin,
            csys_occ_geometry.origin,
            "Matrix origin should match feature occurrence within assembly.",
        )
        self._assert_mat3_almost_equal(
            transformed_csys.orientation, csys_occ_geometry.orientation
        )

    def _assert_mat3_almost_equal(
        self,
        mat_a: geometry.Matrix3x3,
        mat_b: geometry.Matrix3x3,
        places: int | None = None,
    ) -> None:
        """Check that matrices are equal within tolerance."""
        fields = ["Xx", "Xy", "Xz", "Yx", "Yy", "Yz", "Zx", "Zy", "Zz"]
        for field in fields:
            self.assertAlmostEqual(
                getattr(mat_a, field),
                getattr(mat_b, field),
                places=places,
                msg=f"'{field}' field does not match.",
            )
