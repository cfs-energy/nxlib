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
"""Models for NXOpen geometric objects."""

import json
from collections.abc import Sequence
from dataclasses import astuple, dataclass, field, fields
from typing import TYPE_CHECKING, get_origin, get_type_hints

import nxlib
from nxlib import io


class BaseGeometry:
    """Base class for all ``Geometry``."""

    def to_json(self, **kwargs) -> str:
        """Serialize this ``Geometry`` as JSON.

        Parameters
        ----------
        kwargs
            Keyword arguments to ``json.dumps``.

        Returns
        -------
        JSON string for this geometry object.

        """
        return json.dumps(self, **kwargs, cls=io.NxEncoder)

    @classmethod
    def from_json(cls, json_data: str) -> "Geometry":
        """Deserialize a JSON string to a ``Geometry`` model."""
        return json.loads(json_data, cls=io.NxDecoder)

    def __post_init__(self):
        """Type-cast the fields to the proper geometry subclasses."""
        for field_ in fields(self):  # pyright: ignore[reportArgumentType]
            val = getattr(self, field_.name)
            expected_type = get_type_hints(type(self))[field_.name]
            if get_origin(expected_type) is not None or isinstance(val, expected_type):
                # If the expected type is generic (i.e. list[str]) or if we already have
                # the correct type, we don't need to do anything.
                continue

            # Cast to the proper type
            cast_val = (
                expected_type(*val) if isinstance(val, Sequence) else expected_type(val)
            )
            setattr(self, field_.name, cast_val)


_geometry_docstr = """Model for NX-based geometry objects.

All Geometry subclasses have the following requirements:
1. Shall be a ``dataclass`` by way of the ``@dataclass`` decorator.
2. Shall have a name that exactly matches the corresponding ``NXOpen`` geometry object.
For example, ``class Point3d(Geometry)`` corresponds to ``NXOpen.Point3d``."""

# If we are running from the NX interpreter, we give Geometry the
# NxGeometryMixin class, which provides the to_nx and from_nx methods.
if nxlib.status.interpreter_is_nx or TYPE_CHECKING:
    from nxlib.nxopen import nx_geometry

    class Geometry(BaseGeometry, nx_geometry.NxGeometryMixin):
        f"""{_geometry_docstr}.
        
        Includes capabilities to convert to and from NXOpen objects.
        """

else:

    class Geometry(BaseGeometry):
        f"""{_geometry_docstr}"""


@dataclass
class CoordinateSequence:
    """Indicates that the class can be serialized as a sequence of coordinates
    rather than as distinct keys. Makes the class an iterator over its keys.
    This allows for consumers to run code such as np.array(*point).

    """

    def __getitem__(self, position: int) -> float:
        return astuple(self)[position]

    def __len__(self) -> int:
        return len(astuple(self))

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class Point3d(Geometry, CoordinateSequence):
    """Model for NXOpen.Point3d."""

    X: float
    Y: float
    Z: float


@dataclass
class Point4d(Geometry, CoordinateSequence):
    """Model for NXOpen.Point4d."""

    X: float
    Y: float
    Z: float
    W: float


@dataclass
class Matrix3x3(Geometry, CoordinateSequence):
    """Model for NXOpen.Matrix3x3."""

    Xx: float
    Xy: float
    Xz: float
    Yx: float
    Yy: float
    Yz: float
    Zx: float
    Zy: float
    Zz: float


@dataclass
class Vector3d(Geometry, CoordinateSequence):
    """Model for NXOpen.Vector3d."""

    X: float
    Y: float
    Z: float


@dataclass
class Plane(Geometry):
    """Model for NXOpen.Plane."""

    origin: Point3d
    normal: Vector3d


@dataclass
class Line(Geometry):
    """Model for NXOpen.Line."""

    start: Point3d  # NXOpen.Line.StartPoint
    end: Point3d  # NXOpen.Line.EndPoint


@dataclass
class Ellipse(Geometry):
    """Model for NXOpen.Ellipse."""

    major_radius: float
    minor_radius: float
    start_angle: float
    end_angle: float
    rot_angle: float
    center: Point3d
    matrix: Matrix3x3


@dataclass
class Arc(Geometry):
    """Model for NXOpen.Arc."""

    radius: float
    start_angle: float
    end_angle: float
    center: Point3d
    matrix: Matrix3x3


@dataclass
class Spline(Geometry):
    """Model for NXOpen.Spline."""

    order: int  # NXOpen.Spline.Order
    knots: list[float] = field(default_factory=list)  # NXOpen.Spline.GetKnots()
    poles: list[Point4d] = field(default_factory=list)  # NXOpen.Spline.GetPoles()
