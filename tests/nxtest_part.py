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
"""Tests for opening & closing parts."""

import unittest
from pathlib import Path
from typing import Literal

import NXOpen  # pyright: ignore[reportMissingModuleSource]

from nxlib.nxopen.part import (
    ModifiedComponentError,
    _part_open_in_session,
    open_part,
    part_context,
)
from tests.fixtures.common import native


@native
class TestPartContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Set up the test class with the session and the part to test opening."""
        cls.session = NXOpen.Session.GetSession()
        cls.local_file = str(Path(__file__).parent.resolve() / "data" / "model1.prt")
        return super().setUpClass()

    def setUp(self):
        """At the start of each test, make sure test parts are closed."""
        self.assertIsNone(_part_open_in_session(self.local_file, self.session))

    def tearDown(self) -> None:
        """Make sure that any parts opened are closed at the end of each test."""
        self.session.Parts.CloseAll(NXOpen.BasePart.CloseModified.CloseModified, None)

    def _test_part_context(
        self,
        part_path: str,
        on_exit: Literal["close-part", "close-tree", "undisplay"],
        if_modified: Literal["discard", "error"],
        should_close: bool,
        modify_part: bool,
    ) -> None:
        """Open a part, optionally modify it, and test the behavior on close."""
        # Open the part in the context manager under test
        with part_context(
            part_path=part_path, on_exit=on_exit, if_modified=if_modified
        ) as work_part:
            # Make sure the part isn't modified yet.
            self.assertFalse(work_part.IsModified)

            # Optionally perform a modification (just add a new point) and
            # check that the IsModified status changes
            if modify_part:
                work_part.Points.CreatePoint(NXOpen.Point3d(1.0, 2.0, 3.0))  # pyright: ignore[reportCallIssue]
                self.assertTrue(work_part.IsModified)

        # Find the part in the session
        part = _part_open_in_session(self.local_file, self.session)
        if should_close:  # Part should not have been found in session
            self.assertIsNone(part)
        else:  # Part should have been found.
            self.assertIsInstance(part, NXOpen.Part)


class TestPartContextNoPrevious(TestPartContext):
    def test_part_ctx_no_mod_close_discard(self):
        self._test_part_context(
            part_path=self.local_file,
            on_exit="close-part",
            if_modified="discard",
            should_close=True,
            modify_part=False,
        )

    def test_part_ctx_close_when_done_warn(self):
        with (
            self.assertWarns(DeprecationWarning),
            part_context(
                part_path=self.local_file,
                close_when_done=True,
            ) as work_part,
        ):
            # Make sure the part isn't modified yet.
            self.assertFalse(work_part.IsModified)

        # Find the part in the session
        part = _part_open_in_session(self.local_file, self.session)
        self.assertIsNone(part)

    def test_part_ctx_no_mod_close_error(self):
        self._test_part_context(
            part_path=self.local_file,
            on_exit="close-part",
            if_modified="error",
            should_close=True,
            modify_part=False,
        )

    def test_part_ctx_no_mod_undisplay(self):
        self._test_part_context(
            part_path=self.local_file,
            on_exit="undisplay",
            if_modified="discard",
            should_close=False,
            modify_part=False,
        )

    def test_part_ctx_mod_close_discard(self):
        self._test_part_context(
            part_path=self.local_file,
            on_exit="close-part",
            if_modified="discard",
            should_close=True,
            modify_part=True,
        )

    def test_part_ctx_mod_close_error(self):
        with self.assertRaises(ModifiedComponentError):
            self._test_part_context(
                part_path=self.local_file,
                on_exit="close-part",
                if_modified="error",
                should_close=True,
                modify_part=True,
            )


class TestPartContextWithPreviousPart(TestPartContext):
    @classmethod
    def setUpClass(cls) -> None:
        # This part should be open at the start and end of each test.
        cls.prev_part_path = str(
            Path(__file__).parent.resolve() / "data" / "sections.prt"
        )
        return super().setUpClass()

    def setUp(self) -> None:
        """At the start of each test, make sure the part we are testing opening is
        closed. Open this class' previous part in the session."""
        super().setUp()  # get the nx session
        self.assertIsNone(_part_open_in_session(self.prev_part_path, self.session))
        self._prev_part = open_part(self.prev_part_path)

        # Make this class' part the displayed part
        self.session.Parts.SetActiveDisplay(
            self._prev_part,
            NXOpen.DisplayPartOption.AllowAdditional,
            NXOpen.PartDisplayPartWorkPartOption.UseLast,
        )
        self.assertIs(self._prev_part, self.session.Parts.Display)

    def tearDown(self) -> None:
        """Make sure that any parts opened are closed at the end of each test."""
        self.assertIs(self._prev_part, self.session.Parts.Display)
        self._prev_part.Close(
            NXOpen.BasePart.CloseWholeTree.TrueValue,  # pyright: ignore[reportArgumentType]
            NXOpen.BasePart.CloseModified.CloseModified,  # pyright: ignore[reportArgumentType]
            None,  # pyright: ignore[reportArgumentType]
        )
        return super().tearDown()

    def test_part_ctx_undisplay_discard(self):
        self._test_part_context(
            part_path=self.local_file,
            on_exit="undisplay",
            if_modified="discard",
            should_close=False,
            modify_part=False,
        )


class TestPartContextAssembly(TestPartContext):
    @classmethod
    def setUpClass(cls) -> None:
        """Set up the test class with the session and the part to test opening."""
        cls.session = NXOpen.Session.GetSession()
        cls.assy_file = str(Path(__file__).parent.resolve() / "data" / "attr_assy.prt")
        cls.component_files = [
            str(Path(__file__).parent.resolve() / "data" / "model1.prt"),
            str(Path(__file__).parent.resolve() / "data" / "model2.prt"),
        ]
        cls.part_files = [cls.assy_file] + cls.component_files

    def setUp(self):
        """At the start of each test, make sure test parts are closed."""
        for part_file in self.part_files:
            self.assertIsNone(_part_open_in_session(part_file, self.session))

    def tearDown(self) -> None:
        """Make sure that any parts opened are closed at the end of each test."""
        for part_file in self.part_files:
            part = _part_open_in_session(part_file, self.session)
            if part:
                part.Close(
                    NXOpen.BasePart.CloseWholeTree.TrueValue,  # pyright: ignore[reportArgumentType]
                    NXOpen.BasePart.CloseModified.CloseModified,  # pyright: ignore[reportArgumentType]
                    None,  # pyright: ignore[reportArgumentType]
                )

    def _test_assy_context(
        self,
        part_path: str,
        open_assembly: bool,
        on_exit: Literal["close-part", "close-tree", "undisplay"],
        if_modified: Literal["discard", "error"],
        should_close_assy: bool,
        should_close_components: bool,
    ) -> None:
        with part_context(
            part_path=part_path,
            on_exit=on_exit,
            if_modified=if_modified,
            open_assembly=open_assembly,
        ) as work_part:
            self.assertFalse(work_part.IsModified)
            # Check that the components are open and unmodified
            for comp_file in self.component_files:
                comp = _part_open_in_session(comp_file, self.session)
                if open_assembly:
                    self.assertIsInstance(comp, NXOpen.Part)
                    assert comp is not None
                    self.assertFalse(comp.IsModified)
                else:
                    self.assertIsNone(comp)

        assy_comp = _part_open_in_session(self.assy_file, self.session)
        if should_close_assy:
            # Since we just ran close-part, the top level should be closed
            # but the other components should be open
            self.assertIsNone(assy_comp)
        else:
            self.assertIsInstance(assy_comp, NXOpen.Part)
        for comp_file in self.component_files:
            comp = _part_open_in_session(comp_file, self.session)
            if should_close_components:
                self.assertIsNone(comp)
            else:
                self.assertIsInstance(comp, NXOpen.Part)

    def test_part_ctx_assy_full_no_mod_close_tree(self):
        self._test_assy_context(
            self.assy_file,
            open_assembly=True,
            on_exit="close-tree",
            if_modified="discard",
            should_close_assy=True,
            should_close_components=True,
        )

    def test_part_ctx_assy_full_no_mod_close_part(self):
        # Open the component files first, so they're already open in session
        # Otherwise they get closed with the assembly, even if we use "close-part"
        for comp_file in self.component_files:
            open_part(comp_file)
        self._test_assy_context(
            self.assy_file,
            open_assembly=True,
            on_exit="close-part",
            if_modified="discard",
            should_close_assy=True,
            should_close_components=False,
        )

    def test_part_ctx_assy_no_mod_close_tree(self):
        self._test_assy_context(
            self.assy_file,
            open_assembly=False,
            on_exit="close-tree",
            if_modified="discard",
            should_close_assy=True,
            should_close_components=True,
        )

    def test_part_ctx_assy_no_mod_close_part(self):
        self._test_assy_context(
            self.assy_file,
            open_assembly=False,
            on_exit="close-part",
            if_modified="discard",
            should_close_assy=True,
            should_close_components=True,
        )
