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
"""Encoders & decoders for ``nxlib.geometry.Geometry`` models."""

import json
from dataclasses import astuple, fields, is_dataclass
from typing import Any

from nxlib import geometry


class NxEncoder(json.JSONEncoder):
    """JSON encoder for ``Geometry`` models. Serializes models
    and adds a "_type" key such that the models can be deserialized using
    an ``NxDecoder``. ``CoordinateSequence`` instances have their coordinates
    serialized as lists, and all other objects are serialized as ``dict``s.
    """

    def default(self, o):
        # All Geometry subclasses should be a dataclass
        if isinstance(o, geometry.Geometry) and is_dataclass(o):
            # Simplify serialization of coordinate sequences
            if isinstance(o, geometry.CoordinateSequence):
                nx_obj_dict: dict[str, Any] = {"coords": astuple(o)}
            else:
                nx_obj_dict = {
                    field.name: getattr(o, field.name) for field in fields(o)
                }

            # Add a _type key so the NxDecoder knows what class
            # to deserialize into.
            nx_obj_dict["_type"] = type(o).__name__
            return nx_obj_dict
        return super().default(o)


class NxDecoder(json.JSONDecoder):
    """JSON decoder for ``Geometry`` that was previously serialized using
    an ``NxEncoder``. Looks for a "_type" key when decoding objects,
    and instantiates the proper class if that "_type" key is found and valid.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, object_hook=self._decode_nx)

    def _decode_nx(self, obj: dict[str, Any]) -> Any:
        # If the _type key is available, try to instantiate an NxGeometry object.
        # Otherwise use the default JSONDecoder
        obj_type = obj.get("_type")
        if obj_type:
            # See if "_type" corresponds to a known subclass
            geo_subclass = getattr(geometry, obj_type)
            if not isinstance(geo_subclass, type) or not issubclass(
                geo_subclass, geometry.Geometry
            ):
                msg = f"{geo_subclass} is not a subclass of {geometry.Geometry}."
                raise TypeError(msg)
            obj.pop("_type")  # Get rid of this key now that we know what it is
            if "coords" in obj:
                return geo_subclass(*obj["coords"])
            return geo_subclass(**obj)
        return obj
