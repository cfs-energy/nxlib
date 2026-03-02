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
    def to_nx(
        self: "geometry.Arc",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Arc: ...
    @overload
    def to_nx(
        self: "geometry.Ellipse",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Ellipse: ...
    @overload
    def to_nx(
        self: "geometry.Line",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Line: ...
    @overload
    def to_nx(
        self: "geometry.Matrix3x3",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Matrix3x3: ...
    @overload
    def to_nx(
        self: "geometry.Point3d",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Point3d: ...
    @overload
    def to_nx(
        self: "geometry.Point4d",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Point4d: ...
    @overload
    def to_nx(
        self: "geometry.Plane",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Plane: ...
    @overload
    def to_nx(
        self: "geometry.Spline",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Spline: ...
    @overload
    def to_nx(
        self: "geometry.Vector3d",
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpen.Vector3d: ...
