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
import NXOpen  # pyright: ignore[reportMissingModuleSource]
import NXOpen.Assemblies  # pyright: ignore[reportMissingModuleSource]

import nxlib


def component_is_reference(component: NXOpen.Assemblies.Component) -> bool:
    """
    Determine whether an assembly component is 'Reference-Only'.

    A component is reference only if it has the attribute called REFERENCE_COMPONENT
    in the context of its parent assembly.

    NOTE: the parent assembly will be opened, if not already open, when this
    function is called.
    """
    # Make sure the parent is loaded so that we can check whether the component is
    # a reference component
    parent = component.Parent
    if parent is None:
        # Component cannot be reference if it does not have a parent component
        return False
    parent_part = parent.Prototype.OwningPart if parent.Prototype else None

    if parent_part is None or not parent_part.IsFullyLoaded:
        work_part = NXOpen.Session.GetSession().Parts.Work
        work_part.ComponentAssembly.OpenComponents(
            NXOpen.Assemblies.ComponentAssembly.OpenOption.ComponentOnly,  # pyright: ignore[reportArgumentType]
            [parent],
        )

    try:
        # This will return an empty string if it exists.
        _isref = component.GetInstanceStringUserAttribute("REFERENCE_COMPONENT", -1)
    except NXOpen.NXException as err:
        # If the attribute wasn't found, it will say so in the error message.
        # If the error message does not indicate a missing attribute, something
        # else is wrong and we need to raise it
        if "The attribute not found." not in err.args[0]:
            raise
        # If the component does not have the REFERENCE_COMPONENT attribute then
        # it is not reference only.
        return False
    return True


def find_components_in_assembly_tree(
    parent: NXOpen.Assemblies.Component,
    *part_numbers: str,
    skip_ref_comps: bool = True,
) -> list[NXOpen.Assemblies.Component]:
    """Recursively find components within an assembly tree.

    Parameters
    ----------
    parent
        Component to search within.
    part_numbers
        Part numbers of component to search for if using managed (Teamcenter) NX,
        or filename stems if using NX native.
    skip_ref_comps
        Skip components marked as "Reference-only" as well as their entire
        sub-trees. Default ``True``. If ``True``, the entire tree will be opened
        in order to determine which components are reference. Set to ``False`` to
        avoid the side-effect of opening components.

    Returns
    -------
    List of components with matching ``part_number``.

    """
    result = []

    # Cache the filesystem mode to avoid expensive call within the recursion
    nx_filesystem_mode = nxlib.status.nx_filesystem_mode

    def _search(parent: NXOpen.Assemblies.Component) -> None:
        """Inner function to avoid needing result in the main function signature."""
        for child in parent.GetChildren():
            if skip_ref_comps and component_is_reference(child):
                continue
            # NOTE: In managed (Teamcenter) mode, the DB_PART_NO attribute denotes the
            # part number. This attribute is not always present in native NX, so instead
            # the filename stem is matched.
            if nx_filesystem_mode == nxlib.NxFilesystemMode.MANAGED:
                try:
                    child_pn = child.GetStringAttribute("DB_PART_NO")
                except NXOpen.NXException as err:
                    if "The attribute not found." in err.args[0]:
                        print(f"ERROR: {child} has no 'DB_PART_NO' attribute. Skipping")
                        continue
                    raise
            else:
                prototype = child.Prototype
                if not prototype:
                    print(f"ERROR: {child} has no prototype. Skipping")
                    continue
                child_pn = prototype.Name

            if child_pn in part_numbers:
                result.append(child)
            _search(child)

    _search(parent)

    return result
