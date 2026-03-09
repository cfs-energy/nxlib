<!-- Copyright 2026 Commonwealth Fusion Systems (CFS), all rights reserved. -->
<!-- This entire source code file represents the sole intellectual property of CFS. -->
<!--  -->
<!-- Licensed under the Apache License, Version 2.0 (the "License"); -->
<!-- you may not use this file except in compliance with the License. -->
<!-- You may obtain a copy of the License at -->
<!--  -->
<!--     http://www.apache.org/licenses/LICENSE-2.0 -->
<!--  -->
<!-- Unless required by applicable law or agreed to in writing, software -->
<!-- distributed under the License is distributed on an "AS IS" BASIS, -->
<!-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. -->
<!-- See the License for the specific language governing permissions and -->
<!-- limitations under the License. -->
# nxlib
Nxlib is a library and toolkit for enabling workflows that utilize the [NXOpen Python API](https://docs.sw.siemens.com/en-US/doc/209349590/PL20231101866122454.custom_api.nxopen_python_ref). Nxlib has the following core capabilities:

- ✅ Reusable library functions for common NX journaling operations.
- ✅ Utilities for ensuring that nxlib is discoverable by the NX Python interpreter.
- ✅ A test runner to enable unit and integration testing of NXOpen functions and modules.
- ✅ Capability to execute NX journals on a virtual machine for incorporation in CI workflows.

Simply put, nxlib enables automated data extraction from CAD, and much more.

This README and the API documentation are available on [GitHub Pages](https://cfs-energy.github.io/nxlib).

You can learn the basics of using nxlib by working through the [example repository](example/).

# About NXOpen and Journals
An NX journal is a Python script that's run from within NX. A journal is run using the Python interpreter that is bundled into the NX executable.

What makes nxlib valuable is that it manages the interactions between two Python interpreters: the interpreter for your project, and the interpreter that's built into NX. The built-in NX interpreter is limited to Python 3.10 as of NX 2406, and it comes with no third-party packages. All code in the nxlib.nxopen library needs to be runnable in the NX interpreter. Therefore nxlib:

- Has zero production dependencies for code that runs with NXOpen.
- Is _developed and tested_ with Python 3.10.

However, nxlib can still be used as a dependency for projects that use a Python version >3.10, and for projects that depend on other third-party packages. 

# Installation & Setup
## Installation
Add `cfs-nxlib` to your project with uv:
```shell
uv add cfs-nxlib
```
or with pip:
```shell
pip install cfs-nxlib
```

## Setting up your environment variables
NX and Teamcenter licensing and authentication rely on having several environment variables
set up correctly. Most of these environment variables should have been set up with your NX installation, but this is not always the case.

The [.env.sample](.env.sample) file ships with nxlib, and includes the relevant environment variables for using nxlib. Work with your system administrator to fill this out, rename it to `.env`, and place it in the root of your project.

## Linking nxlib to the NX interpreter
Installing a library of functions for use with NXOpen is not as trivial as running `pip install cfs-nxlib`, since the Python interpreter used by NX is not the same as your system-level Python installation or your virtual environment. This presents the challenge of ensuring that `nxlib` will be importable by the NX Python interpreter from your specific NX journal.

The recommended approach is to symbolically link the `nxlib` library to `%UGII_BASE_DIR%/NXBIN/python`, which is on the import search path for the built-in NX Python interpreter. Simply run
```shell
uv run nxlib install
```
This will allow you to `import nxlib` from any NX Python journal, without needing to restart NX or modify any environment variables. This approach is not viable for distribution of standalone scripts.

You can verify that the `nxlib` installation was successful by running 
```shell
uv run nxlib status
```

> ⚠️**CAUTION**:
> You may choose to install `nxlib` into a virtual environment, or it may be installed as a dependency for another project. However, the Python interpreter that runs your journals is still the one that's built into NX. This Python interpreter is **not** part of your virtual environment, and it will not by default be able to import any third party libraries.

> ⚠️**CAUTION**:
> While you can have multiple `nxlib` installations across virtual environments, you can only have *one* symbolic link to `%UGII_BASE_DIR%/NXBIN/python`. If you want to be sure of the nxlib installation you're using, you can run `nxlib status -v`, or you can make a runtime assertion that whichever `nxlib` you imported is the one that NX is using: `assert nxlib.status.nxlib_symlinked`.
>
> You can run `uv run nxlib install --overwrite` to update the symlink, or `uv run nxlib remove` to delete it.

## Setting up Teamcenter Authentication
In addition to needing an NX installation to run, a Teamcenter license is required to run managed NX sessions. You can authenticate to Teamcenter using SSO, or with a username and password. Nxlib will try to authenticate via password if the corresponding `TC_USERNAME`, `TC_PASSWORD`, `TC_PASSWORD_FILE` environment variables are set. You can override this behavior by passing `--auth=[sso|password]` when running `nxlib run` or `nxtest`.

### Single Sign-on (SSO) 
Most end-users of nxlib will use SSO to authenticate. Authenticating with SSO requires having your environment variables set correctly. See the section on environment variables above for enabling SSO.

If you are using SSO, there is nothing you need to do except occasionally authenticate as you normally would when running NX. 

### Username and Password or Password File
If SSO is not an option, nxlib also supports using a Teamcenter username along with a password or encrypted password file. This is not a typical user case for end-users, and is intended to be used for when nxlib is run in CI or on a virtual machine.

To authenticate with a username and password, the `TC_USERNAME` environment variable must be set appropriately, along with at least one of `TC_PASSWORD` or `TC_PASSWORD_FILE`.

# How to run NX Journals
NX journals can be called from within another Python script, from the command line, or from within an existing NX session.

## Running journals from another Python script
In your Python code, you can run:
```python
from nxlib import run_journal

run_journal("path/to/journal.py", ["journal", "arguments"])
```

## Running from the command line
nxlib has a handy command line utility for executing journals. This utility executes journals headlessly, without launching the NX GUI. This makes execution faster for large assemblies, as they do not have to be rendered graphically.

You can run an existing journal:
```shell
uv run nxlib run my_journal.py
```
Or you can just run arbitrary Python code through NX:
```shell
uv run nxlib run -c "from nxlib import nxprint; nxprint('Hello world')"
```
Try `nxlib run --help` for the full set of options.

### Running with a custom Python virtual environment
You can run journals using your own Python virtual environment, including the libraries installed there. This can be done using the `--local` flag on the CLI command, or by setting `local=True` in the `run_journal` function.

This has the limitation in that the minor Python version that NX runs must match that of your local interpreter. As of NX2406, that version is Python 3.10.

## Running from within NX
To run from within NX:

1. In NX, press Alt+F8 to run a journal
2. Click "Browse..." and navigate to the journal file you'd like to run
3. Enter any arguments from the journal, one per line, in the box at the bottom of the window.
4. Click "Run".

# Development
[uv](https://github.com/astral-sh/uv) is recommended for development of nxlib.

## Quickstart
```shell
# Clone the repository
git clone https://github.com/cfs-energy/nxlib.git
```
```shell
# Install nxlib and all dependencies
uv sync --all-extras

# Sync nxlib to the NX Python interpreter
uv run nxlib install

# Run the nxlib unit tests
uv run pytest

# Run the NX-based unit tests
uv run nxtest
```

## Python Version
The Python version used to develop nxlib is constrained to the Python minor version that's built into NX. This ensures that all code will be runnable with the NX interpreter. The `.python-version` file ensures that the correct version is used.

 As of NX 2406, the minor Python version that ships with NX is 3.10. To check the Python version that shipped with your version of NX, run

 ```shell
 uv run nxlib run --native -c "import sys; print(sys.version)"
 ```

 It's recommended to update the `.python-version` file to match your development environment.

## Writing Tests
There are two types of functions you'll want to test: NX journaling functions, and everything else. Tests of NX journaling functions are those tests where one or more test assertions must be made from within the NX Python interpreter. Tests of non-journaling functions, especially those that rely on third-party packages, likely need to be run with your local Python interpreter.

In order to keep test discovery of the two types of tests exclusive, segregate the test files as follows:
- Tests for NX journaling functions should live in files that match the pattern `nxtest*.py`
- Tests for everything else should live in files that match the pattern `test*.py` (as is common for most test suites & runners).

To run all tests, you need to run two separate commands:

```shell
uv run nxtest # Run tests on NX journaling functions
uv run pytest # Run tests on everything else
```

The `nxtest` command runs Python's built in unittest by default. If running with the `--local` flag, you can use `--runner=pytest`. This combination, or `--pytest` for short, is a wrapper for [pytest](https://docs.pytest.org/en/stable/), if pytest is part of your local environment. `nxtest` accepts most regular `unittest discover` and `pytest` command line arguments.

> ✏️**NOTE**:
> By default, `nxtest` runs in native mode. To run in managed Teamcenter mode, pass the `--teamcenter` argument on the command line. If any of your tests specifically require native or managed mode, you can mark your tests with the provided `@native` or `@teamcenter` decorators, respectively:

```python
import unittest

import nxlib
from tests.fixtures.common import native, teamcenter

class MyTests(unittest.TestCase)
    @teamcenter
    def test_that_requires_teamcenter(self):
        ...

    @native
    def test_that_requires_native(self):
        ...
```
> If you have tests that require both native and Teamcenter modes, you'll have to run them separately: `uv run nxtest && uv run nxtest --teamcenter`.

> ✏️**NOTE**:
> When running tests, it's crucial that the NX interpreter is using the same version of nxlib you are. Therefore the test runner will fail if `nxlib.status.nx_simlinked is False`. You can override this behavior with the `--allow-extern-nxlib` flag.

## Adding type stubs & auto-complete for NXOpen in VSCode
You can get type hints and auto-complete for the `NXOpen` package in VSCode by running
```
nxlib typings
```
from your development root. This will copy the contents of `%UGII_BASE_DIR%\UGOPEN\pythonStubs` to your `typings/` folder. In VSCode, ensure that your `python.analysis.stubPath` points to the newly created folder for your workspace.
