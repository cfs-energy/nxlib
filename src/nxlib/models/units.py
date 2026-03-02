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
"""Importable models for physical units."""

from enum import Enum


class PartUnits(Enum):
    """
    Length units for an NX part. This enum mirrors NXOpen.Part.Units.
    See https://docs.sw.siemens.com/en-US/doc/209349590/PL20231101866122454.custom_api.nxopen_python_ref
    for reference.
    """

    INCHES = 0
    MILLIMETERS = 1
    MIX = 2
    METERS = 3
    MICROMETERS = 4

    @property
    def abbreviation(self):
        match self.name:
            case "INCHES":
                return "in"
            case "MILLIMETERS":
                return "mm"
            case "MIX":
                return ""
            case "METERS":
                return "m"
            case "MICROMETERS":
                return "𝜇m"
            case _:
                msg = f"No shortened name for {self}"
                raise NotImplementedError(msg)


class AngleUnits(Enum):
    """
    Angle units available for use in NX measurements and expressions. Reference documentation
    could not be found. The members of this class are instances of ``NXOpen.Unit``. The
    correspondence to the NXOpen model is as follows:

    -------------------------------
    | AngleUnits   | NXOpen.Unit  |
    -------------------------------
    | name         | Name         |
    | value        | Symbol       |
    | abbreviation | Abbreviation |
    """

    Radian = "radians"
    Degrees = "degrees"
    Revs = "revolutions"
    PiRadian = "pi radians"

    @property
    def abbreviation(self):
        match self.name:
            case "Radian":
                return "rad"
            case "Degrees":
                return "°"
            case "Revs":
                return "rev"
            case "PiRadian":
                return "𝜋-rad"
