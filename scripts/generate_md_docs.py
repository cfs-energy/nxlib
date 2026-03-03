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
"""Generate nxlib API documentation as Markdown using pydoc-markdown.

Output is written as one .md file per module under the given build directory,
mirroring the package layout (e.g. nxlib/nxopen/uf.md). No import of nxlib
is required (pydoc-markdown parses source via docspec), so NXOpen need not be
installed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer


def main() -> None:
    parser = argparse.ArgumentParser(
        "generate_md_docs",
        description="Generate nxlib API documentation as Markdown (wiki-friendly).",
    )
    parser.add_argument(
        "build_dir",
        type=Path,
        help="Output directory for Markdown files (e.g. docs_md).",
    )
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    build_dir.mkdir(parents=True, exist_ok=True)

    session = PydocMarkdown()
    loader = session.loaders[0]
    assert isinstance(loader, PythonLoader)
    loader.search_path = ["src"]
    loader.packages = ["nxlib"]

    modules = session.load_modules()
    session.process(modules)

    renderer = session.renderer
    assert isinstance(renderer, MarkdownRenderer)
    renderer.render_toc = True
    renderer.insert_header_anchors = True

    for module in modules:
        out_path = build_dir / f"{module.name.replace('.', '/')}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        md = renderer.render_to_string([module])
        out_path.write_text(md, encoding="utf-8")

    print(f"Wrote {len(modules)} Markdown files under {build_dir}")


if __name__ == "__main__":
    main()
