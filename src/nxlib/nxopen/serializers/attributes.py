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
"""Functions for recursively querying Teamcenter/NX attributes for an assembly
and serializing them as CSV.
"""

import csv
import os
from pathlib import Path

import NXOpen  # pyright: ignore[reportMissingModuleSource]
import NXOpen.Assemblies  # pyright: ignore[reportMissingModuleSource]

from nxlib import nxprint

AssemblyAttributes = dict[str, dict[str, str | None]]


def get_assembly_attributes(
    parent: NXOpen.Assemblies.Component,
    attributes: list[str],
    index_col: str = "DB_PART_NO",
    *,
    found: set[str] | None = None,
    result: AssemblyAttributes | None = None,
) -> AssemblyAttributes:
    """Recursive function to get part attributes for each unique piece
    part in an assembly.

    Parameters
    ----------
    parent
        Parent assembly component from which to query attributes.
    attributes
        List of attributes to query.
    index_col
        Name of the column by which to index the components.
    found
        Set of components for which assembly attributes have already
        been queried.
    result
        Pass-by-reference dictionary of assembly attributes that
        have already been found.

    Returns
    -------
    Nested dictionary, with first level keys being part numbers.
    Second level are attribute keys and their queried values.

    """
    # Check that the parent has a part number attribute. If it doesn't, skip it
    # and return with what we already have.
    result = result or {}
    try:
        parent_pn = parent.GetStringAttribute(index_col)
    except NXOpen.NXException:
        nxprint(f"ERROR: {parent} ('{parent.Name}') has no '{index_col}'!")
        return result

    # Only query attributes from part numbers that haven't been seen yet.
    found = found or set()
    if parent_pn not in found:
        part_attrs: dict[str, str | None] = {index_col: parent_pn}
        for attr in attributes:
            # an NXException is usually generated if an attribute can't
            # be found. In this case we set that attribute to None.
            # We don't log a warning here, since many attributes are legitimately
            # None, such as the mass or material for an assembly.
            try:
                part_attrs[attr] = parent.GetStringAttribute(attr)
            except NXOpen.NXException:
                part_attrs[attr] = None

        # Record the resulting attributes
        result[parent_pn] = part_attrs
        # Add the parent P/N to the list of parts we've already queried
        found.add(parent_pn)

        # Recurse through the child components
        for child in parent.GetChildren():
            get_assembly_attributes(
                child,
                attributes,
                index_col=index_col,
                found=found,
                result=result,
            )

    return result


def write_assembly_attributes(
    attrs: AssemblyAttributes,
    outfile: str | os.PathLike,
    index_col: str = "DB_PART_NO",
) -> Path:
    """Write the attributes of a component or assembly and all its
    unique child components (if any) to a CSV file.

    The first column of the CSV will be "DB_PART_NO", and the remaining
    columns will be the ``attributes`` provided to this function, if they
    exist.

    Parameters
    ----------
    attrs
        The ``AssemblyAttributes`` to write. Assumes that all parts
        share the same set of attributes.
    outfile
        The path to the CSV file to write to
    index_col
        Name of the column by which to index the components.

    Returns
    -------
    The path to the resulting file.

    """
    outfile = Path(outfile)
    first_pn = next(iter(attrs.keys()))
    attribute_names = list(attrs[first_pn].keys())
    with open(outfile, newline="", mode="w") as part_metadata:
        writer = csv.DictWriter(part_metadata, [index_col, *attribute_names])
        writer.writeheader()
        for row in attrs.values():
            writer.writerow(row)

    nxprint(f"Wrote assembly attributes to {outfile}.")

    return outfile
