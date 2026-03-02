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
"""Methods for Teamcenter Authentication."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path


class TcAuthMethod(Enum):
    """Method for Teamcenter authentication."""

    # Choose automatically based on environment variables
    AUTO = "auto"

    # Single sign-on, typically used for developers and users
    # who have NX installed and have a Teamcenter account
    SSO = "sso"

    # Password or password file, typically used by CI runners
    # or virtual machines that aren't tied to a specific persons'
    # Teamcenter account
    PASSWORD = "password"

    def resolve(self) -> TcAuthMethod:
        """Resolve an automatic selection for TC auth method based on the
        users's environment variables. If ``auth_method`` is not set to AUTO,
        simply return it."""
        if self == TcAuthMethod.AUTO:
            return (
                TcAuthMethod.PASSWORD
                if "TC_USERNAME" in os.environ
                and ("TC_PASSWORD" in os.environ or "TC_PASSWORD_FILE" in os.environ)
                else TcAuthMethod.SSO
            )
        return self


def tc_credential_args() -> list[str]:
    """
    Convert Teamcenter credentials into command line arguments for run_journal.exe.

    Your teamcenter credentials must be present in the environment for this to work.
    The ``TC_USERNAME`` variable must be set, along with at least one of ``TC_PASSWORD``
    and ``TC_PASSWORD_FILE``. ``TC_PASSWORD_FILE`` will take precedence over
    ``TC_PASSWORD``.

    Returns
    -------
    List of command line arguments to send to run_journal.exe to set up Teamcenter
    session. If 'password_file' was provided, this will return
    ``['-u=your_username', '-pf=/path/to/pwd/file']``.
    Otherwise will return
    ``['-u=your_username', '-p=open_sesame!']``

    Raises
    ------
    ``KeyError`` if ``TC_USERNAME`` is not set, or if neither ``TC_PASSWORD``
    or ``TC_PASSWORD_FILE`` are not set.
    ``FileNotFoundError`` if ``TC_PASSWORD_FILE`` environment variable
    points to a non-existent file.
    """
    user = os.environ.get("TC_USERNAME")
    if not user:
        raise KeyError("Could not validate TC login credentials: TC_USERNAME not set!")
    password, password_file = (
        os.environ.get("TC_PASSWORD"),
        os.environ.get("TC_PASSWORD_FILE"),
    )
    if password_file:
        pw_file = Path(password_file)
        if not pw_file.exists():
            raise FileNotFoundError("Password file %s not found" % pw_file)
        return [f"-u={user}", f"-pf={str(pw_file.resolve())}"]
    elif password:
        return [
            f"-u={user}",
            f"-p={password}",
        ]
    raise KeyError(
        "Could not validate TC login credentials: one of TC_PASSWORD or TC_PASSWORD_FILE must be set!"
    )
