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
"""nxlib internal status."""

import os
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Optional


class NxExecutionMode(Enum):
    """Execution mode for NX."""

    GRAPHICAL = 1
    """NX is running within the UI."""
    HEADLESS = 2
    """NX is being run from the command line."""
    NO_NX = 3
    """This function was not called from within NX."""


class NxFilesystemMode(Enum):
    """Filesystem mode for NX."""

    NATIVE = 1
    """NX is running from your local filesystem."""
    MANAGED = 2
    """NX is running off of the Teamcenter database."""
    NO_NX = 3
    """This function was not called from within NX."""


class NxHealth(Enum):
    """Health of the NX installation."""

    HEALTHY = 1
    """NX is installed, the headless executable exists, the graphical executable exists,
    and the NX Python path exists."""
    BROKEN = 2
    """NX is installed but some components are missing."""
    NO_NX = 3
    """NX is not installed."""


class NxlibStatus:
    """nxlib status. Useful for runtime checks & logic as well as debugging."""

    def __init__(self, version: str):
        self.nxlib_version = version
        """The version of the nxlib library."""
        self.sys_exc: str = sys.executable
        """Alias for sys.executable, or the path to the Python executable that's 
        running nxlib."""
        self.sys_vers: str = sys.version
        """Alias for sys.version, or the version of the Python interpreter."""

    def __str__(self):
        attrs = [attr for attr in dir(self) if not attr.startswith("_")]
        attrs.sort()
        return "\n".join([f"{key:<25}: {getattr(self, key)}" for key in attrs])

    @property
    def interpreter_is_nx(self) -> bool:
        """Returns ``True`` if nxlib is being run from within an NX interpreter,
        and ``False`` if nxlib is run from within a local Python interpreter."""
        if self.nx_headless_executable is None or self.nx_ui_executable is None:
            return False
        return sys.executable.endswith(
            self.nx_ui_executable.name
        ) or sys.executable.endswith(self.nx_headless_executable.name)

    @property
    def nx_execution_mode(self) -> NxExecutionMode:
        """Determine whether NX is running in the UI or from the command line (headless).
        Returns ``None`` if NX is not running."""
        sys_exec_path = Path(sys.executable).resolve()
        if (
            self.nx_headless_executable is not None
            and Path(self.nx_headless_executable).resolve() == sys_exec_path
        ):
            return NxExecutionMode.HEADLESS
        elif (
            self.nx_ui_executable is not None
            and Path(self.nx_ui_executable).resolve() == sys_exec_path
        ):
            return NxExecutionMode.GRAPHICAL
        return NxExecutionMode.NO_NX

    @property
    def nx_headless_executable(self) -> Optional[Path]:
        """Path to the executable used for running NX journals headlessly."""
        if not self.nx_installed:
            return None
        assert self.ugii_base_dir is not None
        return self.ugii_base_dir / "NXBIN" / "run_journal.exe"

    @property
    def nx_health(self) -> NxHealth:
        """Check whether the local NX installation is healthy."""
        if not self.nx_installed:
            return NxHealth.NO_NX
        return (
            NxHealth.HEALTHY
            if (
                self.nx_python_root is not None
                and self.nx_python_root.exists()
                and self.nx_headless_executable is not None
                and self.nx_headless_executable.exists()
                and self.nx_ui_executable is not None
                and self.nx_ui_executable.exists()
            )
            else NxHealth.BROKEN
        )

    @property
    def nx_installed(self) -> bool:
        """Whether NX is installed in the local system."""
        return self.ugii_base_dir is not None and self.ugii_base_dir.exists()

    @property
    def nx_filesystem_mode(self) -> NxFilesystemMode:
        """Return whether NX is running in a managed Teamcenter Session or native.
        Returns ``None`` if NX is not running."""
        if not self.interpreter_is_nx:
            return NxFilesystemMode.NO_NX
        import NXOpen.UF  # type: ignore

        ufs = NXOpen.UF.Uf()
        return (
            NxFilesystemMode.MANAGED
            if ufs.IsUgmanagerActive()
            else NxFilesystemMode.NATIVE
        )

    @property
    def nx_python_root(self) -> Optional[Path]:
        """``Path`` to the root Python directory in the local machine's NX
        installation."""
        ugii_base_dir = os.environ.get("UGII_BASE_DIR")
        if ugii_base_dir is None:
            return

        return Path(ugii_base_dir).resolve() / "NXBIN" / "python"

    @property
    def nx_ui_executable(self) -> Optional[Path]:
        """Path to the main graphical NX executable."""
        if not self.nx_installed:
            return None
        assert self.ugii_base_dir is not None
        return self.ugii_base_dir / "NXBIN" / "ugraf.exe"

    @property
    def nx_version(self) -> Optional[str]:
        """NX Version."""
        nx_version_search = re.findall(r"\d+$", str(self.ugii_base_dir))
        if nx_version_search:
            nx_version_num = nx_version_search.pop()
            return nx_version_num

    @property
    def nxlib_path(self) -> Path:
        """Path to the runtime installation of nxlib"""
        return Path(__file__).parent.resolve()

    @property
    def nxlib_symlink_path(self) -> Optional[Path]:
        """Path within the NX pythonpath where nxlib is linked."""
        pyroot = self.nx_python_root
        if pyroot is None:
            return

        nx_link_path = pyroot / "nxlib"
        if not nx_link_path.exists():
            return
        return nx_link_path.resolve()

    @property
    def nxlib_symlinked(self) -> bool:
        """Determine whether the running version of nxlib is symbollicaly linked
        to the NX Python interpreter.

        Performing an assertion of this property is
        recommended for all testing and critical operations. Failure to do so may
        mean that NX is using a different version of nxlib than expected."""
        if self.nxlib_symlink_path is None:
            return False
        if self.nxlib_path != self.nxlib_symlink_path:
            return False
        return True

    @property
    def teamcenter_enabled(self) -> bool:
        """Determine whether the system has Teamcenter enabled. This is currently
        based on whether the ``FMS_HOME`` environment variable has been set to
        a valid path.

        This property can also be explicitly overridden by setting
        the ``NXLIB_TC_DISABLE`` environment variable to "true"."""
        if os.environ.get("NXLIB_TC_DISABLE") == "true":
            return False
        fms_home_var = os.environ.get("FMS_HOME")
        if fms_home_var:
            return Path(fms_home_var).exists()
        return False

    @property
    def ugii_base_dir(self) -> Optional[Path]:
        """Return the ``Path`` to the ``UGII_BASE_DIR`` environment variable,
        if it has been set."""
        ugii_base_dir = os.environ.get("UGII_BASE_DIR")
        return Path(ugii_base_dir) if ugii_base_dir else None
