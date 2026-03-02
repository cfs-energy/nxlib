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
"""Functions for interacting with NXOpen.UF (User Functions)."""

import NXOpen  # pyright: ignore[reportMissingModuleSource]
import NXOpen.UF  # pyright: ignore[reportMissingImports]


def get_object_tags_by_name(object_name: str) -> list[int]:
    """Get all tags for objects with a matching name.

    Parameters
    ----------
    object_name
        Name of the feature to get tags for

    Returns
    -------
    The list of tags for objects matching ``object_name``.

    """
    found_tags = []
    # The CycleByName function takes the object name, and the tag of the last object
    # returned by CycleByName, starting with the null tag (0).
    # https://docs.sw.siemens.com/en-US/doc/209349590/PL20231101866122454.custom_api.nxopen_python_ref
    last_found_tag = NXOpen.UF.UFSession.GetUFSession().Obj.CycleByName(object_name, 0)

    # We continue to call CycleByName in the while loop below until it returns 0 again,
    # indicating the end of the cycle.
    while last_found_tag != 0:
        found_tags.append(last_found_tag)
        last_found_tag = NXOpen.UF.UFSession.GetUFSession().Obj.CycleByName(
            object_name,
            last_found_tag,
        )
    return found_tags


def get_group_members(group_tag: int) -> list[tuple[int, NXOpen.TaggedObject]]:
    """Get a list of object tags and objects in a group.

    Parameters
    ----------
    group_tag
        Valid tag for the group to query

    Returns
    -------
    List of tag, object tuples found in the group.

    Raises
    ------
    ``ValueError`` if ``group_tag`` is invalid.
    ``TypeError`` if ``group_tag`` does not refer to an ``NXOpen.Group``.

    """
    if group_tag == 0:  # Null tag not allowed
        msg = "Null tag (0) invalid for get_group_members."
        raise ValueError(msg)
    # Check if group_tag exists
    try:
        obj = NXOpen.TaggedObjectManager.GetTaggedObject(group_tag)
    except SystemError as err:
        msg = f"Tag {group_tag} is invalid."
        raise ValueError(msg) from err

    # Determine if `group_tag` actually represents a group
    if not isinstance(obj, NXOpen.Group):
        msg = f"Tag {group_tag} refers to {type(obj)}, expected NXOpen.Group."
        raise TypeError(msg)

    uf_session = NXOpen.UF.UFSession.GetUFSession()

    # Get the tags for all members of the group
    group_tags, _num_tags = uf_session.Group.AskGroupData(group_tag)

    group_members = []
    # Query the objects associated with each tag in the group.
    for tag in group_tags:
        tagged_obj = NXOpen.TaggedObjectManager.GetTaggedObject(tag)
        group_members.append((tag, tagged_obj))

    return group_members
