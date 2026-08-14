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
from typing import overload

import NXOpen  # pyright: ignore[reportMissingModuleSource]

import nxlib.geometry as geometry

UpdateOption = NXOpen.SmartObject.UpdateOption

class NxGeometryMixin:
    _registry = {}

    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.Arc) -> "geometry.Arc": ...
    @overload
    @classmethod
    def from_nx(
        cls, nx_geometry: NXOpen.CartesianCoordinateSystem
    ) -> "geometry.CartesianCoordinateSystem": ...
    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.Ellipse) -> "geometry.Ellipse": ...
    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.Line) -> "geometry.Line": ...
    @overload
    @classmethod
    def from_nx(
        cls, nx_geometry: NXOpen.Matrix3x3 | NXOpen.NXMatrix
    ) -> "geometry.Matrix3x3": ...
    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.Plane) -> "geometry.Plane": ...
    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.DatumPlane) -> "geometry.Plane": ...
    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.Point3d) -> "geometry.Point3d": ...
    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.Point4d) -> "geometry.Point4d": ...
    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.Spline) -> "geometry.Spline": ...
    @overload
    @classmethod
    def from_nx(cls, nx_geometry: NXOpen.Vector3d) -> "geometry.Vector3d": ...
    @overload
    def to_nx(self: "geometry.Arc", part: NXOpen.Part) -> NXOpen.Arc:
        """Convert to ``NXOpen.Arc``.\n
        :param part: ``NXOpen.Part`` in which to create the Arc."""
    @overload
    def to_nx(
        self: "geometry.CartesianCoordinateSystem",
        part: NXOpen.Part,
        is_temporary: bool = False,
    ) -> NXOpen.CartesianCoordinateSystem:
        """Convert to ``NXOpen.CartesianCoordinateSystem``.\n
        :param part: ``NXOpen.Part`` in which to create the CartesianCoordinateSystem.
        :param is_temporary: Coordinate system is not displayed or saved with the part
         file. Default ``False``."""
    @overload
    def to_nx(self: "geometry.Ellipse", part: NXOpen.Part) -> NXOpen.Ellipse:
        """Convert to ``NXOpen.Ellipse``.\n
        :param part: ``NXOpen.Part`` in which to create the Ellipse."""
    @overload
    def to_nx(self: "geometry.Line", part: NXOpen.Part) -> NXOpen.Line:
        """Convert to ``NXOpen.Line``.\n
        :param part: ``NXOpen.Part`` in which to create the Line."""
    @overload
    def to_nx(self: "geometry.Matrix3x3") -> NXOpen.Matrix3x3:
        """Convert to ``NXOpen.Matrix3x3``."""
    @overload
    def to_nx(self: "geometry.Point3d") -> NXOpen.Point3d:
        """Convert to ``NXOpen.Point3d``."""
    @overload
    def to_nx(self: "geometry.Point4d") -> NXOpen.Point4d:
        """Convert to ``NXOpen.Point4d``."""
    @overload
    def to_nx(
        self: "geometry.Plane",
        part: NXOpen.Part,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Plane:
        """Convert to ``NXOpen.Plane``.\n
        :param part: ``NXOpen.Part`` in which to create the Plane.
        :param update_option: Update geometry for smart objects. Default ``Mixed``."""
    @overload
    def to_nx(
        self: "geometry.Spline",
        part: NXOpen.Part,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Spline:
        """Convert to ``NXOpen.Spline``. Not Implemented."""
    @overload
    def to_nx(self: "geometry.Vector3d") -> NXOpen.Vector3d:
        """Convert to ``NXOpen.Vector3d``."""
