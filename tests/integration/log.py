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
import logging

import nxlib  # noqa: F401

logger = logging.getLogger(__name__)


def main():
    logger.info("This retains INFO level.")
    try:
        1 / 0  # pyright: ignore[reportUnusedExpression]
    except ZeroDivisionError:
        logger.error("This retains ERROR level and full stack trace!", exc_info=True)


if __name__ == "__main__":
    main()
