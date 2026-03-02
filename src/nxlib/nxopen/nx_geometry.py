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
"""Mixin class for converting nxlib.models.geometry.Geometry objects
to and from their corresponding NXOpen geometry objects.
"""

import NXOpen  # pyright: ignore[reportMissingModuleSource]

from nxlib import geometry

NXOpenGeometry = (
    NXOpen.Curve
    | NXOpen.Point3d
    | NXOpen.Point4d
    | NXOpen.Matrix3x3
    | NXOpen.NXMatrix
    | NXOpen.Plane
    | NXOpen.Vector3d
)

UpdateOption = NXOpen.SmartObject.UpdateOption


class NxGeometryMixin:
    """Mixin class for ``nxlib.geometry.Geometry`` that provides methods
    for converting ``Geometry`` objects to and from their corresponding
    NXOpen objects.
    """

    @classmethod
    def from_nx(cls, nx_geometry: NXOpenGeometry) -> "geometry.Geometry":
        """Convert NXOpen geometry elements to ``models.geometry`` classes.

        Parameters
        ----------
        nx_geometry
            ``NXOpen`` geometry with a supported ``Geometry`` subclass.

        """
        target_cls = getattr(geometry, nx_geometry.__class__.__name__)
        if not isinstance(target_cls, type) or not issubclass(
            target_cls, geometry.Geometry
        ):
            msg = f"{target_cls} is not a subclass of {geometry.Geometry}."
            raise TypeError(msg)
        if target_cls is None:
            msg = f"{nx_geometry.__class__} has no analogue in {geometry.__name__}"
            raise TypeError(msg)

        maker_functions = {
            NXOpen.Arc: cls._make_arc,
            NXOpen.Ellipse: cls._make_ellipse,
            NXOpen.Line: cls._make_line,
            NXOpen.Matrix3x3: cls._make_mat3x3,
            NXOpen.NXMatrix: cls._make_mat3x3,
            NXOpen.Plane: cls._make_plane,
            NXOpen.Point3d: cls._make_pt3,
            NXOpen.Point4d: cls._make_pt4,
            NXOpen.Spline: cls._make_spline,
            NXOpen.Vector3d: cls._make_vec3,
        }

        maker_func = maker_functions.get(nx_geometry.__class__)
        if maker_func is not None:
            return maker_func(nx_geometry, target_cls)
        raise NotImplementedError(f"Could not serialize {nx_geometry}.")

    def to_nx(
        self,
        part: NXOpen.Part | None = None,
        update_option: UpdateOption = UpdateOption.Mixed,  # pyright: ignore[reportArgumentType]
    ) -> NXOpenGeometry:
        """Convert ``geometry.Geometry`` to their associated ``NXOpen`` objects.

        Parameters
        ----------
        part
            The ``NXOpen.Part`` object in which to create the object.
            Objects which inherit from ``NXOpen.SmartObject`` can only be created in
            the context of a work part.
        update_option
            When to update the geometry for smart objects. Default ``Mixed``. Ignored for
            primitives such as points and vectors.

        """
        # Check if the part parameter is required
        if issubclass(getattr(NXOpen, self.__class__.__name__), NXOpen.SmartObject):
            if part is None:
                msg = f"Part parameter required to instantiate NXOpen.{self.__class__.__name__}."
                raise ValueError(msg)
            if update_option == NXOpen.SmartObject.UpdateOption.DontUpdate:
                msg = (
                    "NXOpen.SmartObject.UpdateOption.DontUpdate is invalid "
                    "for geometry creation."
                )
                raise ValueError(msg)
            match self:
                case geometry.Plane():
                    return part.Planes.CreatePlane(
                        self.origin.to_nx(),
                        self.normal.to_nx(),
                        update_option,  # pyright: ignore[reportArgumentType]
                    )
                case geometry.Arc():
                    return part.Curves.CreateArc(
                        self.center.to_nx(),
                        part.NXMatrices.Create(self.matrix.to_nx()),
                        self.radius,
                        self.start_angle,
                        self.end_angle,
                    )
                case geometry.Line():
                    return part.Curves.CreateLine(self.start.to_nx(), self.end.to_nx())
                case geometry.Ellipse():
                    return part.Curves.CreateEllipse(
                        self.center.to_nx(),
                        self.major_radius,
                        self.minor_radius,
                        self.start_angle,
                        self.end_angle,
                        self.rot_angle,
                        part.NXMatrices.Create(self.matrix.to_nx()),
                    )
                case geometry.Spline():
                    msg = (
                        '"To create an instance of this object cannot be created at this time."'
                        " - The NXOpen Documentation"
                    )
                    raise NotImplementedError(msg)
                case _:
                    msg = (
                        f"Could not create NXOpen object corresponding to"
                        f" {self.__class__}."
                    )
                    raise NotImplementedError(msg)
        match self:
            case geometry.Matrix3x3():
                return NXOpen.Matrix3x3(*self)
            case geometry.Point3d():
                return NXOpen.Point3d(*self)
            case geometry.Point4d():
                return NXOpen.Point4d(*self)
            case geometry.Vector3d():
                return NXOpen.Vector3d(*self)
            case _:
                msg = (
                    f"Could not create NXOpen object corresponding to {self.__class__}."
                )
                raise NotImplementedError(msg)

    @classmethod
    def _make_arc(cls, arc: NXOpen.Arc, target_cls: type) -> "geometry.Arc":
        return target_cls(
            radius=arc.Radius,
            start_angle=arc.StartAngle,
            end_angle=arc.EndAngle,
            center=cls.from_nx(arc.CenterPoint),
            matrix=cls.from_nx(arc.Matrix.Element),
        )

    @classmethod
    def _make_ellipse(cls, ell: NXOpen.Ellipse, target_cls: type) -> "geometry.Ellipse":
        return target_cls(
            major_radius=ell.MajorRadius,
            minor_radius=ell.MinorRadius,
            start_angle=ell.StartAngle,
            end_angle=ell.EndAngle,
            rot_angle=ell.RotationAngle,
            center=cls.from_nx(ell.CenterPoint),
            matrix=cls.from_nx(ell.Matrix.Element),
        )

    @classmethod
    def _make_line(cls, line: NXOpen.Line, target_cls: type) -> "geometry.Line":
        return target_cls(
            cls.from_nx(line.StartPoint),
            cls.from_nx(line.EndPoint),
        )

    @classmethod
    def _make_mat3x3(
        cls,
        mat: NXOpen.Matrix3x3 | NXOpen.NXMatrix,
        target_cls: type,
    ) -> "geometry.Matrix3x3":
        """Convert an NXOpen.Matrix3x3 or an NXOpen.NXMatrix to a geometry.Matrix3x3.

        If an NXMatrix is passed, NXMatrix.Element will be used,
        which should return the NXOpen.Matrix3x3.
        """
        try:
            mat = mat.Element
        except AttributeError:
            pass
        return target_cls(
            mat.Xx,
            mat.Xy,
            mat.Xz,
            mat.Yx,
            mat.Yy,
            mat.Yz,
            mat.Zx,
            mat.Zy,
            mat.Zz,
        )

    @classmethod
    def _make_plane(cls, plane: NXOpen.Plane, target_cls: type) -> "geometry.Plane":
        """Convert an NXOpen.Plane to a ``geometry.Plane``."""
        return target_cls(cls.from_nx(plane.Origin), cls.from_nx(plane.Normal))

    @classmethod
    def _make_pt3(cls, pt: NXOpen.Point3d, target_cls: type) -> "geometry.Point3d":
        """Convert an NXOpen.Point3d to a tuple."""
        return target_cls(pt.X, pt.Y, pt.Z)

    @classmethod
    def _make_pt4(cls, pt: NXOpen.Point4d, target_cls: type) -> "geometry.Point4d":
        """Convert an NXOpen.Point4d to a tuple."""
        return target_cls(pt.X, pt.Y, pt.Z, pt.W)

    @classmethod
    def _make_spline(cls, spline: NXOpen.Spline, target_cls: type) -> "geometry.Spline":
        return target_cls(
            spline.Order,
            spline.GetKnots(),
            [cls.from_nx(pole) for pole in spline.GetPoles()],
        )

    @classmethod
    def _make_vec3(cls, vec: NXOpen.Vector3d, target_cls: type) -> "geometry.Vector3d":
        """Convert an NXOpen.Vector3d to a tuple."""
        return target_cls(vec.X, vec.Y, vec.Z)
