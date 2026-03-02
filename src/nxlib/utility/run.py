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
"""Run a journal or arbitrary Python code through managed teamcenter."""

import importlib.resources
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

import nxlib
from nxlib.tc_auth import TcAuthMethod, tc_credential_args
from nxlib.utility.common import RunMode


def run_journal(
    journal_path: str | os.PathLike,
    journal_args: Optional[list[str]] = None,
    run_mode: RunMode = "native",
    auth_method: TcAuthMethod = TcAuthMethod.AUTO,
    local: bool = False,
    verbose: bool = False,
) -> int:
    """Run an NX journal headlessly. This function is the main entry point for
    running NXOpen based journals with nxlib. Attempts to set up environment
    variables to match your site-specific configuration for NX and Teamcenter
    licensing & authentication.

    Parameters
    ----------
    journal_path
        Path to the journal file to be run
    journal_args
        Arguments to pass to the journal
    run_mode
        The mode in which to run NX. "native" runs on the local filesystem, and
        "managed" uses the Teamcenter database. Default "native".
    auth_method:
        Method of authentication for Teamcenter session. Defaults to automatic
        discovery.

        If the ``TC_USERNAME`` environment variable is set, along with one of
        ``TC_PASSWORD`` or ``TC_PASSWORD_FILE``, those credentials will be used.
    local
        Use the local Python interpreter rather than the built-in NX Python interpreter.
        Default ``False``.
        <br><br>
        Note that NX can only use an alternate interpreter if it has the same minor
        version as the built-in interpreter. For example, as of this writing the built-in
        interpreter is Python 3.10.12, but we can use an alternate interpreter up to
        3.10.16. You'll get an error such as "Error loading libraries needed to run a
        journal" if you try to run with Python > 3.10.
        <br><br>
        If an entirely different python interpreter is desired, you can specify this
        by setting the "UGII_PYTHON_LIBRARY" and "UGII_PYTHONPATH" environment variables.
    verbose
        Show detailed log messages. Default ``False``.

    Returns
    -------
    Return code from run_journal.exe.
    """
    # Check that NX is installed and that the journal to be run exists
    if not nxlib.status.nx_installed:
        raise nxlib.NxNotInstalledError("NX is not installed on this system.")

    journal_path = Path(journal_path)
    if not journal_path.exists():
        raise FileNotFoundError("Could not locate Python journal %s" % journal_path)

    # Path to the run_journal executable relative to UGII_BASE_DIR
    run_journal_exe_path = nxlib.status.nx_headless_executable
    if run_journal_exe_path is None or not run_journal_exe_path.exists():
        raise FileNotFoundError("Could not locate %s" % run_journal_exe_path)

    # Set up the environment variables for TC/NX execution
    _set_env_vars(auth_method, verbose)

    if local:
        _set_env_local_python()

    # Start building the command to execute
    exec_args = [
        str(run_journal_exe_path.resolve()),  # fully qualified path to run_journal.exe
    ]
    if run_mode == "managed":
        exec_args.append("-pim")  # run in managed mode
        if verbose:
            print(f"Using {auth_method.resolve()}")
        if auth_method.resolve() == TcAuthMethod.PASSWORD:
            exec_args.extend(tc_credential_args())

    exec_args.append(str(journal_path.resolve()))  # path to journal to be run

    if journal_args:
        exec_args.append("-args")
        exec_args.extend(journal_args)

    if verbose:
        print(f"Running {' '.join(exec_args)}")
    res = subprocess.run(exec_args)
    return res.returncode


def run_python(
    src: str,
    dir: Optional[str | os.PathLike] = None,
    append_path: bool = True,
    threaded: bool = True,
    keep_script: bool = False,
    **kwargs,
) -> int:
    """Run arbitrary python code in NX.

    Parameters
    ----------
    src
        Python code to run
    dir
        Working directory from which to call the python code.
    append_path
        Append the system path with the nxlib source directory. Default ``True``.
    threaded
        Set up the NX interpreter to run threaded extension modules such as numpy. See
        https://docs.sw.siemens.com/en-US/doc/209349590/PL20220512394070742.nxopen_prog_guide/xid1124929
        for full explanation.
    keep_script
        Keep the source code that was generated by this function. Default ``False``.
    kwargs
        Keyword arguments to pass to the ``run_journal`` function.
    """
    tmp_journal = tempfile.NamedTemporaryFile(
        "w", suffix=".py", dir=dir or Path(__file__).parent, delete=False
    )
    module_path = str(Path(__file__).parents[1].resolve()).replace("\\", "\\\\")
    with open(tmp_journal.name, "w") as journal:
        if threaded:
            journal.write("#nx: threaded\n")
        if append_path:
            journal.write("import sys\n")
            journal.write("sys.path.append('%s')\n" % module_path)
        journal.write(src)
    try:
        return run_journal(tmp_journal.name, **kwargs)
    finally:
        tmp_journal.close()
        if not keep_script:
            os.unlink(tmp_journal.name)


def _set_env_vars(auth_method: TcAuthMethod, verbose: bool) -> None:
    """Set up the environment variables in order for NX and Teamcenter to execute.

    Attempts to load environment variables from a .env file. If the .site-env file
    was included in the "utility" module of the nxlib distribution, the environment
    variables from this file will be used. The .site-env file is intended to have
    environment variables specific to the user's NX and Teamcenter installation,
    authentication, and licensing.

    If the .site-env file is not found, environment variables will be loaded from
    the .env file in the project root, if it exists.

    Parameters
    ----------
    auth_method
        Authentication method for Teamcenter
    verbose
        Show detailed log messages. Default ``False``.
    """
    # Attempt to load site-specific environment variables that are packaged with nxlib
    if importlib.resources.is_resource("nxlib.utility", ".site-env"):
        with importlib.resources.path("nxlib.utility", ".site-env") as envfile:
            if verbose:
                print(f"Loading environment from {envfile.resolve()}")
            load_dotenv(dotenv_path=envfile)
    else:  # Fallback to default .env file if it exists
        if verbose:
            print("Loading environment from default path...")
        load_dotenv()

    if auth_method.resolve() != TcAuthMethod.SSO:
        # These SSO environment variables may be specified in the .env file. Teamcenter
        # will try to authenticate using SSO if these are set, so if we are planning
        # on using a username/password, we need to manually unset them first.
        os.environ["ENABLE_SSO"] = "false"
        for sso_var in ["NX_SSO_URL", "NX_SSO_APP_ID", "TCSSO_SESSION_AGENT_PATH"]:
            os.environ.pop(sso_var, None)


def _set_env_local_python() -> None:
    """Set the environment variables so that the local Python interpreter will be used,
    instead of the Python interpreter that's built into NX. This allows limited use of
    third-party libraries within NX."""
    sys.path.append(str(nxlib.status.nx_python_root))
    os.environ["UGII_PYTHON_LIBRARY_DIR"] = sys.base_prefix
    os.environ["UGII_PYTHONPATH"] = ";".join(sys.path)
