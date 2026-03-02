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
"""Journal for example nxlib repository.

This journal opens a part file and serializes all points
in the file."""

import argparse
import json
import os
from pathlib import Path

from nxlib import nxprint
from nxlib.geometry import Point3d
from nxlib.io import NxEncoder
from nxlib.nxopen.part import part_context


def get_points(part_file: str | os.PathLike, output_file: str | os.PathLike):
    # Set up the dictionary that we'll serialize
    data = {"points": []}
    nxprint(f"Opening part file from {part_file}...")

    # part_context is a context manager for opening an NX part,
    # similar to Python's built-in open function for opening a
    # regular file.
    with part_context(part_file) as work_part:
        nxprint(f"{work_part.Name} was opened successfully!")
        nxprint("Iterating through points in file.")

        # We iterate through the points that were included in the part file
        for point in work_part.Points:  # type: ignore
            # Each point has a Coordinates property that is an NXOpen.Point3d.
            # We construct an nxlib.geometry.Point3d model directly from the NX object.
            pt = Point3d.from_nx(point.Coordinates)
            data["points"].append(pt)

    # Now we open the output file to write our data
    nxprint("Serializing point data...")
    with open(output_file, "w") as output:
        # We can simply use json.dump to our open file handle here.
        # Note that we need to use cls=NxEncoder to ensure that everything
        # that was converted from nxopen.geometry.Geometry objects gets
        # serialized correctly, and can be deserialized with an nxlib.io.NxDecoder
        json.dump(data, output, cls=NxEncoder, indent=2)

    nxprint(f"{len(data['points'])} points written to {output_file}.")


if __name__ == "__main__":
    # Argparse is used to create a clean command line interface for running the journal
    # with the run_journal function.
    parser = argparse.ArgumentParser("nxlib example")
    parser.add_argument(
        "part_file", type=Path, help="Part file to extract points from."
    )
    parser.add_argument(
        "output_file", type=Path, help="Output file for serialized points."
    )
    args = parser.parse_args()
    get_points(args.part_file, args.output_file)
