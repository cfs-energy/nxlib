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

from __future__ import annotations

import NXOpen  # pyright: ignore[reportMissingModuleSource]

from nxlib import geometry

MathUtils = NXOpen.Session.GetSession().MathUtils
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
            NXOpen.CartesianCoordinateSystem: cls._make_csys,
            NXOpen.DatumPlane: cls._make_plane,
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
        is_temporary: bool = False,
    ) -> NXOpenGeometry:
        """Convert ``geometry.Geometry`` to their associated ``NXOpen`` objects.

        Parameters
        ----------
        part
            The ``NXOpen.Part`` object in which to create the object.
            Objects which inherit from ``NXOpen.SmartObject`` can only be created in
            the context of a work part.
        update_option
            When to update the geometry for smart objects. Default ``Mixed``. Ignored
            for primitives such as points and vectors.
        is_temporary
            Whether ``NXOpen.CartesianCoordinateSystem``s should be temporary, meaning
            they are not displayed or saved with the part file. Default ``False``.

        Returns
        -------
        ``NXOpen`` object corresponding to this ``geometry.Geometry`` object.

        """
        # Check if the part parameter is required
        if issubclass(getattr(NXOpen, self.__class__.__name__), NXOpen.SmartObject):
            if part is None:
                msg = (
                    "Part parameter required to instantiate "
                    f"NXOpen.{self.__class__.__name__}."
                )
                raise ValueError(msg)
            if update_option == NXOpen.SmartObject.UpdateOption.DontUpdate:
                msg = (
                    "NXOpen.SmartObject.UpdateOption.DontUpdate is invalid "
                    "for geometry creation."
                )
                raise ValueError(msg)
            match self:
                # TODO: Add support for NXOpen.DatumPlane
                case geometry.Plane():
                    return part.Planes.CreatePlane(
                        self.origin.to_nx(),
                        self.normal.to_nx(),
                        update_option,  # pyright: ignore[reportArgumentType]
                    )
                case geometry.CartesianCoordinateSystem():
                    return part.CoordinateSystems.CreateCoordinateSystem(
                        self.origin.to_nx(),
                        self.orientation.to_nx(),
                        is_temporary,
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

    def transform(
        self,
        translation: NXOpen.Point3d
        | NXOpen.Vector3d
        | "geometry.Point3d"
        | "geometry.Vector3d"
        | None,
        rotation: NXOpen.Matrix3x3 | "geometry.Matrix3x3" | None,
    ) -> "geometry.Geometry":
        """Transform a geometry object with a translation and rotation.

        Parameters
        ----------
        translation
            Translation vector or point.
        rotation
            Rotation matrix.

        Returns
        -------
        Transformed geometry. For ``nxlib.geometry.CoordinateSequence`` objects,
        a new object is returned. All other `nxlib.geometry.Geometry`` subclasses
        are modified in place.

        Raises
        ------
        ``TypeError`` for invalid translation or rotation objects.
        ``NotImplementedError`` for objects that could not be transformed.

        """
        # Convert the translation to a NXOpen.Vector3d
        match translation:
            case NXOpen.Point3d():
                transvec = MathUtils.ConvertPoint3ToVector3(translation)
            case geometry.Point3d():
                transvec = MathUtils.ConvertPoint3ToVector3(translation.to_nx())
            case geometry.Vector3d():
                transvec = translation.to_nx()
            case NXOpen.Vector3d():
                transvec = translation
            case None:  # Zero translation
                transvec = NXOpen.Vector3d(0.0, 0.0, 0.0)  # pyright: ignore[reportCallIssue]
            case _:
                msg = f"Invalid translation object: {translation}"
                raise TypeError(msg)

        # Convert the rotation to an NXOpen.Matrix3x3
        match rotation:
            case geometry.Matrix3x3():
                rotmat = rotation.to_nx()
            case NXOpen.Matrix3x3():
                rotmat = rotation
            case None:  # Identity matrix, no rotation
                rotmat = NXOpen.Matrix3x3(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)  # pyright: ignore[reportCallIssue]
            case _:
                msg = f"Invalid rotation object: {rotation}"
                raise TypeError(msg)

        # Class-specific transformation
        match self:
            case geometry.Arc() | geometry.Ellipse():
                self.center = _transform_point3d(self.center.to_nx(), transvec, rotmat)
                self.matrix = _transform_matrix3x3(self.matrix.to_nx(), rotmat)
            case geometry.CartesianCoordinateSystem():
                self.origin = _transform_point3d(self.origin.to_nx(), transvec, rotmat)
                self.orientation = _transform_matrix3x3(
                    self.orientation.to_nx(), rotmat
                )
            case geometry.Line():
                self.start = _transform_point3d(self.start.to_nx(), transvec, rotmat)
                self.end = _transform_point3d(self.end.to_nx(), transvec, rotmat)
            case geometry.Matrix3x3():
                return _transform_matrix3x3(self.to_nx(), rotmat)
            case geometry.Plane():
                self.origin = _transform_point3d(self.origin.to_nx(), transvec, rotmat)
                self.normal = _transform_vector3d(self.normal.to_nx(), rotmat)
            case geometry.Point3d():
                return _transform_point3d(self.to_nx(), transvec, rotmat)
            case geometry.Vector3d():
                return _transform_vector3d(self.to_nx(), rotmat)
            case _:
                # TODO: Add support for spline transformation
                msg = f"Unsupported type for transform: {self}"
                raise NotImplementedError(msg)

        return self

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
    def _make_csys(
        cls, csys: NXOpen.CartesianCoordinateSystem, target_cls: type
    ) -> "geometry.CartesianCoordinateSystem":
        return target_cls(
            origin=cls.from_nx(csys.Origin),
            orientation=cls.from_nx(csys.Orientation.Element),
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
    def _make_plane(
        cls, plane: NXOpen.Plane | NXOpen.DatumPlane, target_cls: type
    ) -> "geometry.Plane":
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


def _transform_point3d(
    point: NXOpen.Point3d, transvec: NXOpen.Vector3d, rotmat: NXOpen.Matrix3x3
) -> "geometry.Point3d":
    """Transform a Point3d with a given vector and rotation matrix."""
    return geometry.Point3d.from_nx(
        MathUtils.AddPoint3ToVector3(
            MathUtils.Multiply(MathUtils.TransposeMatrix3(rotmat), point), transvec
        )
    )  # type: ignore


def _transform_vector3d(
    vector: NXOpen.Vector3d, rotmat: NXOpen.Matrix3x3
) -> "geometry.Vector3d":
    """Transform a Vector3d with a given rotation matrix."""
    return geometry.Vector3d.from_nx(
        MathUtils.Multiply(MathUtils.TransposeMatrix3(rotmat), vector)
    )  # type: ignore


def _transform_matrix3x3(matrix: NXOpen.Matrix3x3, rotmat: NXOpen.Matrix3x3):
    """Transform a Matrix3x3 with a given rotation matrix."""
    return geometry.Matrix3x3.from_nx(
        MathUtils.MultiplyMatrix3AndMatrix3(rotmat, matrix)
    )
