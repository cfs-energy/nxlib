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
from pathlib import Path

import pytest

import nxlib
from nxlib.utility import install as instl


class PatchSubprocessRun:
    """Patch for subprocess.run.

    Parameters:
    -----------
    capture:
        Pass-by-reference dictionary that will capture all arguments
        and keyword arguments passed to subprocess.run
    args:
        Arguments passed to subprocess.run
    retcode:
        The desired return code (default 0)
    kwargs:
        Keyword arguments passed to subprocess.run

    Usage
    -----
    ```python
    capture = {} # will be populated when subprocess.run is called
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: PatchSubprocessRun(capture, *args, **kwargs),
    )
    ```
    """

    def __init__(self, capture: dict, *args, retcode: int = 0, **kwargs):
        self.args = args
        self.returncode = retcode
        self.kwargs = kwargs
        capture.update(self.__dict__)


class TestInstall:
    def test_install_no_nx(self, monkeypatch):
        """Should raise an error if we try to install on a system where NX
        is not installed."""
        # Make it look like NX is not installed
        monkeypatch.delenv("UGII_BASE_DIR", raising=False)

        with pytest.raises(nxlib.NxNotInstalledError):
            instl.install_to_nx()

    def test_install(self, monkeypatch, tmp_path):
        """Test that the correct mklink command will get run."""
        capture = {}
        monkeypatch.setattr(
            "subprocess.run",
            lambda *args, **kwargs: PatchSubprocessRun(capture, *args, **kwargs),
        )
        ugii_tmp = tmp_path
        nxlib_dir = ugii_tmp / "NXBIN" / "python" / "nxlib"
        monkeypatch.setenv("UGII_BASE_DIR", str(ugii_tmp))

        res = instl.install_to_nx()
        assert capture["args"][0][0] == "mklink"
        assert capture["args"][0][-1] == str(nxlib.status.nxlib_path.resolve())
        assert capture["args"][0][-2] == str(nxlib_dir.resolve())
        assert res == 0

    @pytest.mark.parametrize("overwrite", [True, False])
    def test_install_overwrite(self, monkeypatch, tmp_path, overwrite):
        """Test that overwrite flag works as expected."""
        monkeypatch.setattr(
            "subprocess.run",
            lambda *args, **kwargs: PatchSubprocessRun({}, *args, **kwargs),
        )
        ugii_tmp = tmp_path
        nxlib_dir = tmp_path / "NXBIN" / "python" / "nxlib"
        nxlib_dir.mkdir(parents=True)

        monkeypatch.setenv("UGII_BASE_DIR", str(ugii_tmp))

        if overwrite:
            assert instl.install_to_nx(overwrite=overwrite) == 0
        else:
            with pytest.raises(FileExistsError):
                instl.install_to_nx(overwrite=overwrite)


class TestInstallTypings:
    def test_install_typings_no_nx(self, monkeypatch):
        """Should raise an error if we try to install on a system where NX
        is not installed."""
        # Make it look like NX is not installed
        monkeypatch.delenv("UGII_BASE_DIR", raising=False)
        with pytest.raises(nxlib.NxNotInstalledError):
            instl.install_typings("no_dir")

    def test_install_typings_missing(self, monkeypatch, tmp_path):
        """Should raise an error if NX is installed but we can't find the typings dir."""
        # Make it look like NX is installed
        ugii_tmp = tmp_path
        monkeypatch.setenv("UGII_BASE_DIR", str(ugii_tmp))
        with pytest.raises(FileNotFoundError):
            instl.install_typings(".")

    def test_install_typings(self, monkeypatch, tmp_path, capsys):
        """Test a dry run of the typing installation"""
        # Make it look like NX is installed
        ugii_tmp = tmp_path
        monkeypatch.setenv("UGII_BASE_DIR", str(ugii_tmp))
        # Make a fake typing stubs directory
        typings_dir = ugii_tmp / "UGOPEN" / "pythonStubs"
        typings_dir.mkdir(parents=True)

        # Command should succeed with a dry run (don't actually run shutil.copytree)
        assert instl.install_typings(".", dry_run=True) == 0

        # The target and source directories should be in the output
        captured = capsys.readouterr()
        assert str(typings_dir.resolve()) in captured.out
        assert str(Path(".").resolve()) in captured.out


class TestUninstall:
    def test_uninstall_no_nx(self, monkeypatch):
        """Should raise an error if we try to install on a system where NX
        is not installed."""
        # Make it look like NX is not installed
        monkeypatch.delenv("UGII_BASE_DIR", raising=False)
        with pytest.raises(nxlib.NxNotInstalledError):
            instl.uninstall_from_nx()

    def test_uninstall(self, monkeypatch, tmp_path):
        """Test that the correct rmdir command is executed."""
        capture = {}
        monkeypatch.setattr(
            "subprocess.run",
            lambda *args, **kwargs: PatchSubprocessRun(capture, *args, **kwargs),
        )
        ugii_tmp = tmp_path
        nxlib_dir = ugii_tmp / "NXBIN" / "python" / "nxlib"
        nxlib_dir.mkdir(parents=True)
        monkeypatch.setenv("UGII_BASE_DIR", str(ugii_tmp))

        res = instl.uninstall_from_nx()
        assert capture["args"][0][0] == "rmdir"
        assert capture["args"][0][-1] == str(nxlib_dir.resolve())
        assert res == 0

    def test_uninstall_not_linked(self, monkeypatch, tmp_path):
        ugii_tmp = tmp_path
        monkeypatch.setenv("UGII_BASE_DIR", str(ugii_tmp))

        with pytest.raises(FileNotFoundError):
            instl.uninstall_from_nx()
