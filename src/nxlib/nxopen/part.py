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
import warnings
from collections.abc import Generator
from contextlib import contextmanager
from typing import Literal

import NXOpen  # type: ignore
import NXOpen.Assemblies  # type: ignore


class ModifiedComponentError(Exception):
    """Attempt to close a part that has been modified."""


@contextmanager
def part_context(
    part_path: str | os.PathLike,
    on_exit: Literal["close-part", "close-tree", "undisplay"] = "close-part",
    if_modified: Literal["discard", "error"] = "discard",
    **kwargs,
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
    on_exit:
        Action to take when the context manager exits. ``"close-part"`` (default) will
        close only the part that was opened. ``"close-tree"`` will close the part and
        any of its components which were not already opened. ``"undisplay"`` will leave
        the part open, and set the sessions work & display part back to whatever it was
        when this context manager was entered.
    if_modified:
        Action to take if part(s) are to be closed on context manager exit.
        ``"discard"`` (default) will close without saving changes.  ``"error"`` will
        raise a ``ModifiedComponentError``.
    close_when_done:
        (Deprecated) Close the part once the context manager exits, and return to the
        part that was displayed when the context manager was entered. Equivalent
        to ``on_exit="close-part", if_modified="discard"``
    kwargs:
        Keyword arguments to ``nxlib.nxopen.part.open_part``

    Yields
    ------
    The ``NXOpen.Part`` that was returned from ``nxlib.nxopen.part.open_part``.

    Raises
    ------
    ``ModifiedComponentError`` if attempting to close a modified component and
    ``if_modified="error"``.
    """
    # TODO: Remove backwards compatibility for previous APIs
    if "close_when_done" in kwargs:
        msg = (
            "close_when_done is deprecated. To use this behavior in the future,"
            ' please use on_exit="close-part" and if_modified="discard".'
        )
        warnings.warn(msg, DeprecationWarning)
        if kwargs.get("close_when_done"):
            on_exit, if_modified = "close-part", "discard"
            kwargs.pop("close_when_done")  # Don't pass this to open_part
    nx_session = NXOpen.Session.GetSession()  # type: NXOpen.Session
    original_part = nx_session.Parts.Display
    part = open_part(part_path, **kwargs)
    try:
        yield part
    finally:
        if on_exit == "close-part" or on_exit == "close-tree":
            close_whole_tree = (
                NXOpen.BasePart.CloseWholeTree.TrueValue
                if on_exit == "close-tree"
                else NXOpen.BasePart.CloseWholeTree.FalseValue
            )
            close_modified = (
                NXOpen.BasePart.CloseModified.CloseModified
                if if_modified == "discard"
                else NXOpen.BasePart.CloseModified.DontCloseModified
            )
            if part.IsModified and if_modified == "error":
                msg = f"Part '{part.Name}' is modified!"
                raise ModifiedComponentError(msg)
            if not part.IsModified or (part.IsModified and if_modified == "discard"):
                part.Close(
                    close_whole_tree,  # pyright: ignore[reportArgumentType]
                    close_modified,  # pyright: ignore[reportArgumentType]
                    None,  # pyright: ignore[reportArgumentType]
                )
        elif on_exit == "undisplay":
            part.Undisplay()
        # Go back to the original part when the context manager exits
        if original_part is not None:
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

    # Start by checking if the part is already open in the session
    work_part = _part_open_in_session(part_path, nx_session)

    # Set the load options depending on `open_assembly`
    nx_session.Parts.LoadOptions.ComponentsToLoad = (
        NXOpen.LoadOptions.LoadComponents.All
        if open_assembly
        else NXOpen.LoadOptions.LoadComponents.NotSet
    )

    if work_part:
        # If already open, set the part as the actively displayed / work part.
        nx_session.Parts.SetActiveDisplay(
            work_part,
            NXOpen.DisplayPartOption.AllowAdditional,
            NXOpen.PartDisplayPartWorkPartOption.UseLast,
        )
    else:
        # See if the part exists
        try:
            work_part, _status = nx_session.Parts.OpenActiveDisplay(
                part_path, NXOpen.DisplayPartOption.AllowAdditional
            )
        except NXOpen.NXException as err:
            # We need to read the error message to see if we're failing
            # because the object wasn't found, or if a different exception was raised.
            if "object does not exist" in err.args[0]:
                raise FileNotFoundError("Object not found: %s" % part_path)
            # If some other failure, raise it
            raise

    if load_wavelink_parents:
        work_part.LoadWaveLinkFeatureParents()

    return work_part


def _part_open_in_session(
    part_path: str, nx_session: NXOpen.Session
) -> NXOpen.Part | None:
    """Check if a part is open in the current NX session, and return it if it's open.

    Parameters
    ----------
    part_path
        Path or DB_PART_NO for the part to check for.
    nx_session
        The current NX session.

    Returns
    -------
    The part if it was already open, otherwise ``None``.

    """
    try:
        # Check to see if the part is already opened in the session.
        # If it isn't, NX will throw an NXException
        part = nx_session.Parts.FindObject(part_path)
    except NXOpen.NXException as err:
        if "No object found with this name" in err.args[0]:
            return None
        raise
    return part
