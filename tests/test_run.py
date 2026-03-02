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
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

import nxlib
from nxlib.tc_auth import tc_credential_args
from nxlib.utility import run


@pytest.mark.parametrize(
    "creds, expected",
    [
        (  # Happy Path
            {"TC_USERNAME": "elmur_fudd", "TC_PASSWORD": "wabbit!"},
            "-u=elmur_fudd -p=wabbit!".split(),
        ),
        (  # password file takes precedence over password
            {
                "TC_USERNAME": "elmur_fudd",
                "TC_PASSWORD_FILE": __file__,
                "TC_PASSWORD": "wabbit!",
            },
            ["-u=elmur_fudd", "-pf=" + str(Path(__file__).resolve())],
        ),
        (  # Error: no TC_USERNAME
            {"TC_PASSWORD": "wabbit!"},
            KeyError,
        ),
        (  # Error: no password or file
            {"TC_USERNAME": "elmur_fudd"},
            KeyError,
        ),
        (  # Error: password file missing
            {"TC_USERNAME": "elmur_fudd", "TC_PASSWORD_FILE": "/not/here/not/anywhere"},
            FileNotFoundError,
        ),
    ],
)
def test_tc_creds_userpass(creds, monkeypatch, expected):
    """Test that TC credential arguments work as expected given system's
    environment variables."""

    # Patch the variables that were passed in, or delete them if
    # they are present on the system running the test.
    env_vars = "TC_USERNAME TC_PASSWORD TC_PASSWORD_FILE".split()
    for var in env_vars:
        if var in creds:
            monkeypatch.setenv(var, creds[var])
        else:
            monkeypatch.delenv(var, raising=False)

    if isinstance(expected, list):
        assert tc_credential_args() == expected
    else:
        with pytest.raises(expected):
            tc_credential_args()


@pytest.mark.skipif(not nxlib.status.nx_installed, reason="only run if NX is installed")
@pytest.mark.parametrize(
    "run_mode, local",
    [("native", True), ("native", False), ("managed", True), ("managed", False)],
)
def test_run_journal(run_mode, local):
    if run_mode == "managed" and not nxlib.status.teamcenter_enabled:
        pytest.skip(reason="Teamcenter is not enabled.")
    journal_path = Path(__file__).parent / "integration" / "hello.py"
    result = nxlib.run_journal(journal_path, run_mode=run_mode, local=local)
    assert result == 0


@pytest.mark.skipif(not nxlib.status.nx_installed, reason="only run if NX is installed")
def test_run_python():
    python_code = "from nxlib import nxprint; nxprint('hello world')"
    result = nxlib.run_python(python_code, run_mode="native", local=False)
    assert result == 0


def test_set_env_local_python(monkeypatch):
    monkeypatch.delenv("UGII_PYTHON_LIBRARY_DIR", raising=False)
    monkeypatch.delenv("UGII_PYTHONPATH", raising=False)
    run._set_env_local_python()
    assert os.environ["UGII_PYTHONPATH"] == ";".join(sys.path), (
        "UGII_PYTHONPATH should be set to local interpreter's sys.path"
    )
    assert os.environ["UGII_PYTHON_LIBRARY_DIR"] == sys.base_prefix, (
        "UGII_PYTHON_LIBRARY_DIR should be set to the local interpreter's base prefix."
    )
    if nxlib.status.nx_installed:
        assert str(nxlib.status.nx_python_root) in sys.path, (
            "NX interpreter Python path should be in system path."
        )


def test_set_env_vars_site(monkeypatch, env_file):
    """Test that the .site-env is used if present."""
    contents = "TEST_ENV_VAR=platypus"
    dotenv_path = env_file(contents)

    def _patched_load_dotenv(*_args, **kwargs):
        load_dotenv(dotenv_path=kwargs.get("dotenv_path") or dotenv_path)

    monkeypatch.setattr(run, "load_dotenv", _patched_load_dotenv)
    monkeypatch.setattr(
        "nxlib.utility.run.importlib.resources.is_resource", lambda *_args: True
    )
    monkeypatch.setattr(
        "nxlib.utility.run.importlib.resources.path", lambda *_args: dotenv_path
    )
    run._set_env_vars(run.TcAuthMethod.AUTO, False)
    assert os.environ["TEST_ENV_VAR"] == "platypus", (
        "Environment variables should be set"
    )


@pytest.mark.parametrize(
    "auth_method", [run.TcAuthMethod.SSO, run.TcAuthMethod.PASSWORD]
)
def test_set_env_vars_local(monkeypatch, env_file, auth_method):
    """Test that local .env file is used if site env doesn't exist."""
    contents = "TEST_ENV_VAR=platypus"
    sso_vars = ["NX_SSO_URL", "NX_SSO_APP_ID", "TCSSO_SESSION_AGENT_PATH"]
    for n, sso_var in enumerate(sso_vars):
        contents = contents + f"\n{sso_var}=Test_{n}"
    dotenv_path = env_file(contents)

    def _patched_load_dotenv(*_args, **kwargs):
        load_dotenv(dotenv_path=kwargs.get("dotenv_path") or dotenv_path)

    monkeypatch.setattr(run, "load_dotenv", _patched_load_dotenv)
    monkeypatch.setattr(
        "nxlib.utility.run.importlib.resources.is_resource", lambda *_args: False
    )
    run._set_env_vars(auth_method, False)
    assert os.environ["TEST_ENV_VAR"] == "platypus", (
        "Environment variables should be set"
    )
    for var in sso_vars:
        if auth_method is run.TcAuthMethod.SSO:
            assert var in os.environ.keys(), "SSO env vars should remain"
        else:
            assert var not in os.environ.keys(), "SSO env vars should have been deleted"


@pytest.fixture
def env_file(tmp_path):
    def _env_file(contents: str):
        env_path = tmp_path / ".env"
        with open(env_path, "w") as env_fp:
            env_fp.write(contents)
        return env_path

    return _env_file
