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
import pytest

from nxlib.tc_auth import TcAuthMethod


@pytest.mark.parametrize(
    "creds, auth, resolved",
    [
        (
            {"TC_USERNAME": "elmur_fudd", "TC_PASSWORD": "wabbit!"},
            TcAuthMethod.AUTO,
            TcAuthMethod.PASSWORD,
        ),
        ({}, TcAuthMethod.AUTO, TcAuthMethod.SSO),
        ({}, TcAuthMethod.SSO, TcAuthMethod.SSO),
        ({}, TcAuthMethod.PASSWORD, TcAuthMethod.PASSWORD),
    ],
)
def test_auth_method(monkeypatch, creds, auth, resolved):
    # Patch the variables that were passed in, or delete them if
    # they are present on the system running the test.
    env_vars = "TC_USERNAME TC_PASSWORD TC_PASSWORD_FILE".split()
    for var in env_vars:
        if var in creds:
            monkeypatch.setenv(var, creds[var])
        else:
            monkeypatch.delenv(var, raising=False)

    assert auth.resolve() == resolved
