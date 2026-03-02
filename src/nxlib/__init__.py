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
.. include:: ../../README.md
   :start-after: nxlib
"""

import os

# The version of nxlib is dynamic because nxlib does not get properly
# installed to the NX Python interpreter. Instead, nxlib is
# put onto the NX Python interpreter's module search path. This means
# that using importlib.metadata to detect the version will not
# work from within NX.
#
# A test_version unit test exists to ensure that this dynamic
# version and the version listed in pyproject.toml match.
__version__ = "0.5.0"


from ._status import (
    NxExecutionMode,
    NxFilesystemMode,
    NxHealth,
    NxlibStatus,
)
from .exceptions import NxNotInstalledError

status = NxlibStatus(__version__)
# NOTE: models.geometry has conditional logic that depends on status.interpreter_is_nx.
# Therefore the nxlib status has to be initialized prior to importing models.geometry.
from . import geometry  # noqa: E402, I001


__all__ = [
    "geometry",
    "NxlibStatus",
    "NxExecutionMode",
    "NxFilesystemMode",
    "NxHealth",
    "NxNotInstalledError",
]


if status.interpreter_is_nx or "NXLIB_DOCGEN" in os.environ:
    # We can import things that require NXOpen to run
    from . import models as models
    from . import nxopen as nxopen
    from .nxopen.common import nxprint as nxprint

    __all__.extend(["models", "nxopen"])

if not status.interpreter_is_nx:
    # Here we import utility functions that won't be available to or needed by the
    # NX intepreter
    from .utility.run import run_journal as run_journal
    from .utility.run import run_python as run_python

    __all__.extend(["run_journal", "run_python"])
