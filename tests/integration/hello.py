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
"""
Simple integration / smoke-test. Used to ensure that
journals can be run with nxlib. Print nxlib status to the
terminal or listing window.
"""

import sys

import nxlib
from nxlib import nxprint

nxprint(nxlib.status)

args = sys.argv[1:]
if args:
    for a in args:
        nxprint(f"Hello {a}!")
else:
    nxprint("Hello World!")
