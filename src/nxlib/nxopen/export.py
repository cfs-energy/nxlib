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
"""Functions for exporting data to the local filesystem."""

import os
from pathlib import Path

import NXOpen  # type: ignore


def export_expressions(
    part: NXOpen.Part,
    outfile: str | os.PathLike,
) -> Path:
    """
    Export the expressions for the ``Part``. Equivalent to
    Tools -> Expressions -> Export Expressions.

    Parameters
    ----------
    part:
        Part to export expressions from.
    outfile:
        File path to export expressions to.

    Returns
    -------
    Filepath to where expressions were exported.
    """
    outfile = Path(outfile)
    part.Expressions.ExportToFile(
        NXOpen.ExpressionCollection.ExportMode.WorkPart,  # pyright: ignore
        str(outfile),
        NXOpen.ExpressionCollection.SortType.AlphaNum,  # pyright: ignore
    )

    return outfile
