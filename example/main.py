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
"""This is the main script for the nxlib example.

This script controls the overall workflow for opening the part file,
calling the NX journal, and then analyzing the serialized data."""

import argparse
import json
import os
from pathlib import Path

# Third party library imports that would fail if attempting to import
# from within the NX interpreter.
import matplotlib.pyplot as plt
import numpy as np

from nxlib import run_journal
from nxlib.io import NxDecoder


def convert_xyz_to_rz(pts_xyz: np.ndarray) -> np.ndarray:
    """Convert XYZ coordinates to RZ coordinates projected onto the phi=0 plane."""
    return np.array(
        [
            np.linalg.norm(pts_xyz[:, :2], axis=1),  # R is the norm of X and Y coords
            pts_xyz[:, 2],  # Z coordinate is unchanged
        ]
    )


def decode_points(
    part_file: str | os.PathLike, output_file: str | os.PathLike, preview: bool = False
) -> Path:
    """Run an NX journal to extract points from a part file, then convert the points
    from cartesian to polar coordinates, projecting them all onto a single plane. Plot
    the points and return the resulting image."""
    # The first step is to run the journal to extract the points
    # using the run_journal function. This opens a separate process that
    # runs NX headlessly.
    print("Running NX journal to extract points...\n")

    # As a best practice, always use fully-qualified paths when working with NX.
    points_file = Path("points.json").resolve()

    # The run_journal function will return a non-zero exit code if there is
    # a failure during journal execution. It's best practice to check for it.
    exit_code = run_journal(
        "nx_get_points.py",
        journal_args=[str(Path(part_file).resolve()), str(points_file)],
    )
    if exit_code == 0:
        print("\nJournal execution completed successfully.\n")
    else:
        print(f"\nJournal execution failed with exit code {exit_code}.")
        exit(exit_code)

    # Now that we have the data, we can load it with our local Python interpreter
    print(f"Deserializing points from {points_file}...")
    with open(points_file) as point_data:
        # Note that we deserialize using the nxlib.io.NxDecoder, which makes
        # each point into an nxlib.geometry.Point3d object
        data = json.load(point_data, cls=NxDecoder)

    # Now that we're out of the NX interpreter, we can use numpy, a third party library
    # that utilizes compiled extension modules, to perform numerical analysis
    print("Done. Converting to poloidal coordinates...")
    points = np.array(data["points"])
    points_poloidal = convert_xyz_to_rz(points)

    # We'll use matplotlib to plot the data, and write the resulting plot
    # to a PNG file. Maybe that file will have a secret message for us!
    print("Plotting...")
    fig, ax = plt.subplots()
    ax.set_aspect("equal")
    ax.plot(points_poloidal[0], points_poloidal[1], "o", color="#CF6D46", markersize=1)
    ax.axis("off")
    fig.savefig(str(output_file))
    print(f"Saved output to {output_file}")

    # Automatically open the result to see what's in it as long as we aren't
    # running the the test suite
    if preview:
        os.startfile(output_file)

    return Path(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("nxlib example")
    parser.add_argument(
        "part_file",
        type=Path,
        help="Part file to extract points from.",
    )
    parser.add_argument("output_file", type=Path, help="Path to output file.")
    parser.add_argument(
        "--preview", action="store_true", help="Automatically open the result."
    )
    args = parser.parse_args()
    decode_points(args.part_file, args.output_file, args.preview)
