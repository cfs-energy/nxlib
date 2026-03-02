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
import math
import random
import unittest

import nxlib

native = unittest.skipUnless(
    nxlib.status.nx_filesystem_mode == nxlib.NxFilesystemMode.NATIVE,
    reason="Test must be run with NX native",
)

teamcenter = unittest.skipUnless(
    nxlib.status.nx_filesystem_mode == nxlib.NxFilesystemMode.MANAGED,
    reason="Test must be run with managed (Teamcenter) mode",
)


def rand_coords(n: int) -> list[float]:
    """Random n-coordinate float sequence."""
    return [random.uniform(-10_000, 10_000) for _ in range(n)]


def rand_norm_vec() -> list[float]:
    """Random normal vector."""
    vec = [random.random() for _ in range(3)]
    length = math.sqrt(sum(c**2 for c in vec))
    return [v / length for v in vec]


def rand_orthonormal_mat3() -> list[float]:
    """Random orthonormal 3x3 matrix."""
    # Random angles for roll, pitch, and yaw
    a = random.uniform(0, 2 * math.pi)
    b = random.uniform(0, 2 * math.pi)
    c = random.uniform(0, 2 * math.pi)

    # Precompute trig values
    cos_a, sin_a = math.cos(a), math.sin(a)
    cos_b, sin_b = math.cos(b), math.sin(b)
    cos_c, sin_c = math.cos(c), math.sin(c)

    # Combined rotation matrix (Rz * Ry * Rx) flatted in row-major order
    return [
        cos_b * cos_c,
        sin_a * sin_b * cos_c - cos_a * sin_c,
        cos_a * sin_b * cos_c + sin_a * sin_c,
        cos_b * sin_c,
        sin_a * sin_b * sin_c + cos_a * cos_c,
        cos_a * sin_b * sin_c - sin_a * cos_c,
        -sin_b,
        sin_a * cos_b,
        cos_a * cos_b,
    ]
