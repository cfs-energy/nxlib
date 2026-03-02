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
"""Functions for working with assemblies."""

import os
from collections.abc import Generator
from contextlib import contextmanager

import NXOpen  # type: ignore
import NXOpen.Assemblies  # type: ignore


@contextmanager
def part_context(
    part_path: str | os.PathLike, close_when_done: bool = True, **kwargs
) -> Generator[NXOpen.Part, None, None]:
    """
    Open a part in a context manager, and optionally close it when done,
    returning to the part that was previously open.

    Parameters
    ----------
    part_path:
        If running in managed (Teamcenter) mode, this is the part
        number in the form of "@DB/1235467/A". If running natively,
        this is a path to the .prt file.
    close_when_done:
        Close the part once the context manager exits, and return to the
        part that was displayed when the context manager was entered.
    kwargs:
        Keyword arguments to ``nxlib.nxopen.part.open_part``

    Yields
    ------
    The ``NXOpen.Part`` that was returned from ``nxlib.nxopen.part.open_part``.
    """
    nx_session = NXOpen.Session.GetSession()  # type: NXOpen.Session
    original_part = nx_session.Parts.Display if close_when_done else None
    part = open_part(part_path, **kwargs)
    try:
        yield part
    finally:
        # Go back to the original part when the context manager exits
        if original_part is not None and original_part is not part:
            # Close the part that we opened
            part.Undisplay()

            # Set the original part as the displayed part
            part = NXOpen.Part.Null
            nx_session.Parts.SetActiveDisplay(
                original_part,
                NXOpen.DisplayPartOption.AllowAdditional,
                NXOpen.PartDisplayPartWorkPartOption.UseLast,
            )

            # clean-up graphics
            nx_session.CleanUpFacetedFacesAndEdges()


def open_part(
    part_path: str | os.PathLike,
    open_assembly: bool = False,
    load_wavelink_parents: bool = False,
) -> NXOpen.Part:
    """Open a part and return it as the work part.

    Parameters
    ----------
    part_path:
        If running in managed (Teamcenter) mode, this is the part
        number in the form of "@DB/1235467/A". If running natively,
        this is a path to the .prt file.
    open_assembly:
        Open the full assembly. Equivalent to right clicking on the top
        level component and selection Open -> Assembly. Default ``False``.
    load_wavelink_parents:
        Load parents of any WAVE linked features in the part. Default ``False``.

    Returns
    -------
    The part if it could be opened successfully

    Raises
    ------
    ``FileNotFound`` error when attempting to open a part that doesn't exist.
    """
    nx_session = NXOpen.Session.GetSession()  # type: NXOpen.Session

    if isinstance(part_path, os.PathLike):
        part_path = str(part_path.resolve())

    try:
        nx_session.Parts.SetNonmasterSeedPartData(part_path)
    except NXOpen.NXException as err:
        # We need to read the error message to see if we're failing
        # because the object wasn't found, or if a different exception was raised.
        if "object does not exist" in err.args[0]:
            raise FileNotFoundError("Object not found: %s" % part_path)
        # If some other failure, raise it
        raise

    try:
        # Check to see if the part is already opened in the session.
        # If it isn't, NX will throw an NXException
        part1 = nx_session.Parts.FindObject(part_path)
    except NXOpen.NXException:
        # If the part wasn't found, open it.
        nx_session.Parts.OpenActiveDisplay(
            part_path,
            NXOpen.DisplayPartOption.AllowAdditional,
        )
    else:
        nx_session.Parts.SetActiveDisplay(
            part1,
            NXOpen.DisplayPartOption.AllowAdditional,
            NXOpen.PartDisplayPartWorkPartOption.UseLast,
        )

    work_part = nx_session.Parts.Work
    nx_session.CleanUpFacetedFacesAndEdges()

    # RootComponent will be None if part is not an assembly. Otherwise we want to
    # open it fully
    if work_part.ComponentAssembly.RootComponent is not None and open_assembly:
        components_to_open = [work_part.ComponentAssembly.RootComponent]

        work_part.ComponentAssembly.OpenComponents(
            NXOpen.Assemblies.ComponentAssembly.OpenOption.WholeAssembly,  # type: ignore
            components_to_open,
        )

    if load_wavelink_parents:
        work_part.LoadWaveLinkFeatureParents()

    return work_part
