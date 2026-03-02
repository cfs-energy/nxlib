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
"""Test that nxlib.models.geometry classes can be serialized & deserialized."""

import json
from math import pi
from random import random

import pytest

from nxlib import geometry
from tests.fixtures.common import rand_coords, rand_norm_vec, rand_orthonormal_mat3


@pytest.mark.parametrize(
    "geo_cls, seq_len",
    [
        (geometry.Matrix3x3, 9),
        (geometry.Point3d, 3),
        (geometry.Point4d, 4),
        (geometry.Vector3d, 3),
    ],
)
def test_coordseq_roundtrip(geo_cls, seq_len):
    """Test JSON roundtrip for CoordinateSequence."""

    coords = rand_coords(seq_len)
    model = geo_cls(*coords)
    model_serialized = model.to_json()

    model_default_json = json.loads(model_serialized)
    assert model_default_json["_type"] == geo_cls.__name__, (
        "The serialized model should have a _type key that indicates "
        "the source class, which can be used to deserialize to the correct subclass."
    )

    model_deserialized = geometry.Geometry.from_json(model_serialized)
    assert isinstance(model_deserialized, geo_cls), (
        "Should deserialize into the correct class."
    )
    assert isinstance(model_deserialized, geometry.CoordinateSequence), (
        "Should be a subclass of CoordinateSequence."
        " This assertion also acts as a typeguard for the individual coordinate"
        " assertion below."
    )

    for i, c in enumerate(coords):
        assert model_deserialized[i] == c, "Deserialized object should match exactly."


def test_plane_roundtrip():
    """Test JSON roundtrip for Plane."""
    model = geometry.Plane(
        geometry.Point3d(*rand_coords(3)), geometry.Vector3d(*rand_norm_vec())
    )
    model_serialized = model.to_json()
    model_default_json = json.loads(model_serialized)
    assert model_default_json["_type"] == "Plane", (
        "The serialized model should have a _type key that indicates "
        "the source class, which can be used to deserialize to the correct subclass."
    )
    model_deserialized = geometry.Geometry.from_json(model_serialized)
    assert isinstance(model_deserialized, geometry.Plane), (
        "Should deserialize into the correct class."
    )

    assert model_deserialized.origin == model.origin
    assert model_deserialized.normal == model.normal


def test_line_roundtrip():
    """Test JSON roundtrip for Line."""
    model = geometry.Line(
        geometry.Point3d(*rand_coords(3)), geometry.Point3d(*rand_coords(3))
    )
    model_serialized = model.to_json()
    model_default_json = json.loads(model_serialized)
    assert model_default_json["_type"] == "Line", (
        "The serialized model should have a _type key that indicates "
        "the source class, which can be used to deserialize to the correct subclass."
    )
    model_deserialized = geometry.Geometry.from_json(model_serialized)
    assert isinstance(model_deserialized, geometry.Line), (
        "Should deserialize into the correct class."
    )

    assert model_deserialized.start == model.start
    assert model_deserialized.end == model.end


def test_arc_roundtrip():
    """Test JSON roundtrip for Arc."""
    model = geometry.Arc(
        radius=random() * 1000,
        start_angle=random() * pi * 2,
        end_angle=random() * pi * 2,
        center=geometry.Point3d(*rand_coords(3)),
        matrix=geometry.Matrix3x3(*rand_orthonormal_mat3()),
    )
    model_serialized = model.to_json()
    model_default_json = json.loads(model_serialized)
    assert model_default_json["_type"] == "Arc", (
        "The serialized model should have a _type key that indicates "
        "the source class, which can be used to deserialize to the correct subclass."
    )
    model_deserialized = geometry.Geometry.from_json(model_serialized)
    assert isinstance(model_deserialized, geometry.Arc), (
        "Should deserialize into the correct class."
    )

    assert model_deserialized.start_angle == model.start_angle
    assert model_deserialized.radius == model.radius
    assert model_deserialized.end_angle == model.end_angle
    assert model_deserialized.center == model.center
    assert model_deserialized.matrix == model.matrix


def test_ellipse_roundtrip():
    """Test JSON roundtrip for Ellipse."""
    model = geometry.Ellipse(
        major_radius=random() * 1000,
        minor_radius=random() * 1000,
        start_angle=random() * pi * 2,
        end_angle=random() * pi * 2,
        rot_angle=random() * pi * 2,
        center=geometry.Point3d(*rand_coords(3)),
        matrix=geometry.Matrix3x3(*rand_orthonormal_mat3()),
    )
    model_serialized = model.to_json()
    model_default_json = json.loads(model_serialized)
    assert model_default_json["_type"] == "Ellipse", (
        "The serialized model should have a _type key that indicates "
        "the source class, which can be used to deserialize to the correct subclass."
    )
    model_deserialized = geometry.Geometry.from_json(model_serialized)
    assert isinstance(model_deserialized, geometry.Ellipse), (
        "Should deserialize into the correct class."
    )

    assert model_deserialized.start_angle == model.start_angle
    assert model_deserialized.minor_radius == model.minor_radius
    assert model_deserialized.major_radius == model.major_radius
    assert model_deserialized.end_angle == model.end_angle
    assert model_deserialized.rot_angle == model.rot_angle
    assert model_deserialized.center == model.center
    assert model_deserialized.matrix == model.matrix


def test_spline_roundtrip():
    """Test JSON roundtrip for Spline."""
    model = geometry.Spline(
        order=2,
        knots=[0, 0, 1, 0],
        poles=[geometry.Point4d(*rand_coords(4)), geometry.Point4d(*rand_coords(4))],
    )
    model_serialized = model.to_json()
    model_default_json = json.loads(model_serialized)
    assert model_default_json["_type"] == "Spline", (
        "The serialized model should have a _type key that indicates "
        "the source class, which can be used to deserialize to the correct subclass."
    )
    model_deserialized = geometry.Geometry.from_json(model_serialized)
    assert isinstance(model_deserialized, geometry.Spline), (
        "Should deserialize into the correct class."
    )

    assert model_deserialized.order == model.order
    assert model_deserialized.poles == model.poles
    assert model_deserialized.knots == model.knots
