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
"""Functions for installing and uninstalling nxlib to NX."""

import os
import shutil
import subprocess
from pathlib import Path

import nxlib


def install_to_nx(overwrite: bool = False) -> int:
    """Create a directory symbolic link from the NX Python path to nxlib.

    Parameters
    ----------
    overwrite
        Replace an existing symbolic link with a new one. Default ``False``

    Returns
    -------
    Return code for ``mklink`` command.

    Raises
    ------
    ``FileExistsError`` if the link already exists and ``overwrite is False``.
    ``nxlib.NxNotInstalledError`` if NX is not installed to this system.
    """
    if not nxlib.status.nx_installed:
        raise nxlib.NxNotInstalledError("No NX installation detected.")

    # Path to nxlib library modules
    nx_py_path = nxlib.status.nx_python_root
    assert nx_py_path is not None
    nxlib_target_path = nxlib.status.nxlib_path

    # Path where symlink will be created
    nx_link_path = nx_py_path / "nxlib"
    if nx_link_path.exists():
        if overwrite:
            uninstall_from_nx()
        else:
            raise FileExistsError(
                "nxlib is already linked from %s to %s"
                % (nxlib.status.nxlib_symlink_path, nx_link_path)
            )

    args = [
        "mklink",
        "/J",
        "/D",
        str(nx_link_path),
        str(nxlib_target_path),
    ]
    print("Running '%s'..." % " ".join(args))

    result = subprocess.run(args, shell=True)

    return result.returncode


def install_typings(
    development_base: str | os.PathLike, overwrite: bool = False, dry_run: bool = False
) -> int:
    """
    Copy the typings from the NXOpen installation to your development environment.

    Parameters
    ----------
    development_base
        Path to where typings should be installed. This should match your
        ``python.analysis.stubPath`` setting in VSCode.
    overwrite
        Overwrite existing typings, default ``False``.
    dry_run
        Show the source and destination files, but do not copy anything.

    Raises
    ------
    ``PermissionError``, commonly on Windows if files already exist.
    ``FileExistsError`` if directory exists and ``overwrite`` is ``False``.
    ``nxlib.NxNotInstalledError`` if NX is not installed to this system.
    """
    if not nxlib.status.nx_installed:
        raise nxlib.NxNotInstalledError(
            "NX is not installed to this system, and typings are not available."
        )

    assert nxlib.status.ugii_base_dir is not None
    typings_dir = nxlib.status.ugii_base_dir / "UGOPEN" / "pythonStubs"
    if not typings_dir.exists():
        raise FileNotFoundError(
            "NX is installed, but the typings directory was not found at %s"
            % typings_dir
        )

    print("Copying %s to %s ..." % (typings_dir, Path(development_base).resolve()))
    if not dry_run:
        try:
            shutil.copytree(
                typings_dir, development_base, symlinks=False, dirs_exist_ok=overwrite
            )
        except shutil.Error as err:
            raise PermissionError(err)
        print("Typings installed to %s" % Path(development_base).resolve())
    return 0


def uninstall_from_nx() -> int:
    """Remove the directory symbolic link to nxlib from the NX Python path."""
    if nxlib.status.nx_python_root is None:
        raise nxlib.NxNotInstalledError(
            "No NX installation detected, nxlib was never installed. Aborted."
        )
    nx_link_path = nxlib.status.nx_python_root / "nxlib"
    if not nx_link_path.exists():
        raise FileNotFoundError("NX installed, but nxlib is not. Aborted.")
    print("Removing existing nxlib installation from %s..." % nx_link_path)
    args = [
        "rmdir",
        str(nx_link_path),
    ]
    print("Running ", args)
    result = subprocess.run(args, shell=True)
    return result.returncode


def show_install_status():
    """Print the installation status of NXLib."""
    pyroot = nxlib.status.nx_python_root
    if pyroot is None:
        print("NX is not installed on this system.")
        return

    nx_link_path = pyroot / "nxlib"
    if nx_link_path.exists():
        print("nxlib path: %s" % nx_link_path.resolve())
        print("nxlib symlinked to: %s" % nx_link_path)
        if not nxlib.status.nxlib_symlinked:
            print(
                "NOTE: A version of nxlib different from this one is currently installed to NX!"
            )
    else:
        print(
            "nxlib is not installed to NX, and can be installed by running 'nxlib install'."
        )
