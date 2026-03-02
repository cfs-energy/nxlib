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
"""Common functions useful for all NX Journals"""

import os
from typing import Any, Optional

import NXOpen  # type: ignore


def nxprint(
    *values: Any,
    sep: str = " ",
    file: Optional[str | os.PathLike] = None,
):
    """Print to the listing window.

    Parameters
    ----------
    values:
        Data to print.
    sep:
        Separator between values, default " ".
    file:
        Optional file path to write to.
    """
    listing_window = NXOpen.Session.GetSession().ListingWindow
    if file:
        listing_window.SelectDevice(NXOpen.ListingWindow.DeviceType.File, str(file))
    listing_window.Open()
    output = sep.join((str(v) for v in values))
    listing_window.WriteFullline(output)
    listing_window.Close()
    if file:
        listing_window.SelectDevice(NXOpen.ListingWindow.DeviceType.Window, "")
