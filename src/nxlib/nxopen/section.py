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
"""Functions work working with sections and section curves in NX."""

import NXOpen  # pyright: ignore[reportMissingModuleSource]

from nxlib.nxopen.uf import get_group_members, get_object_tags_by_name


def create_section_curves(
    part: NXOpen.Part,
    plane: NXOpen.Plane,
    section_name: str = "NEW_SECTION",
    delete_section: bool = True,
) -> list[tuple[str, list[NXOpen.Curve]]]:
    """Create a copy of section curves for all visible components
    in an assembly.

    Parameters
    ----------
    part
        The part to pull the section curves from
    plane
        The section plane
    section_name
        The optional name of the section, defaults to "NEW_SECTION"
    delete_section
        Whether to delete the section creating a copy of the section
        curves. Default ``True``

    Returns
    -------
    List of 2-tuple representing the section curves for each individual
    component in the assembly. The first item for each tuple is the part number,
    and the second item is a list of section curves for that component instance.

    Note that it's common to have multiple instances of the same component / part
    number within an assembly, and the return type keeps these instances separated.

    """
    section_name = section_name or "NEW_SECT_CURVES"

    # Check that we don't already have a section or object
    # with the name we've chosen. If we do, we won't be able to find
    # our section curves again when we're done.
    if len(get_object_tags_by_name(section_name)) >= 1:
        msg = (
            f"Work part already has section named '{section_name}'. "
            "Please specify a different name for your section curves!"
        )
        raise ValueError(msg)

    dyn_sect_builder = part.DynamicSections.CreateSectionBuilder(
        NXOpen.Display.DynamicSection.Null,
        part.ModelingViews.WorkView,
    )
    dyn_sect_builder.SetName("TMP_SECTION")
    dyn_sect_builder.SetPlane(plane.Origin, plane.Origin, plane.Matrix)

    # Save the section curves so we can interrogate them later
    dyn_sect_builder.SaveCurves(section_name)
    tmp_section = dyn_sect_builder.Commit()

    # Optionally delete the section view so it won't show up later
    if delete_section:
        part.DynamicSections.DeleteSections(False, [tmp_section])  # pyright: ignore[reportArgumentType]

    # Find the tag for the section we just created
    sect_curves_group_tags = get_object_tags_by_name(section_name)

    # Return an empty list if the group couldn't be found; this means there
    # was no visible geometry where the section was created.
    if len(sect_curves_group_tags) < 1:
        return []

    curves = []
    for subgroup_tag, subgroup in get_group_members(sect_curves_group_tags.pop()):
        subgroup_name = subgroup.Name
        subgroup_curves = [curve for _tag, curve in get_group_members(subgroup_tag)]
        curves.append((subgroup_name, subgroup_curves))

    return curves
