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
"""Function for working within managed Teamcenter."""

import NXOpen  # type: ignore
import NXOpen.UF  # type: ignore


def get_latest_revision(db_part_no: str | int) -> str:
    """
    Get the latest revision of a P/N from the Teamcenter database.

    Parameters
    ----------
    db_part_no:
        Part number in Teamcenter database

    Returns
    -------
    String in the form of "@DB/<db_part_number>/<latest_rev>" which represents
    a fully-qualified revision that can be opened.

    Raises
    ------
    ``FileNotFoundError`` if the part does not exist in the database.
    """
    db_part_no = str(db_part_no)
    uf_session = NXOpen.UF.UFSession.GetUFSession()

    # Get the database tag for the requested part
    part_tag = uf_session.Ugmgr.AskPartTag(db_part_no)
    if part_tag == 0:
        # Part tag will be zero if it doesn't exist
        raise FileNotFoundError("Part number %s not found." % db_part_no)

    # Get a list of database tags for the part revisions
    _num_revs, rev_tags = uf_session.Ugmgr.ListPartRevisions(part_tag)

    # Get the latest rev letter/number for the most recent revision
    latest_rev = uf_session.Ugmgr.AskPartRevisionId(rev_tags[-1])

    # Build a string suitable for opening parts
    db_pn_with_rev = "@DB/" + db_part_no + "/" + latest_rev

    return db_pn_with_rev
