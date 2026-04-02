# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.6.0] - 2026-04-02

### Added
- Added the `nxlib.geometry.CartesianCoordinateSystem` class, which mirrors the `NXOpen.CartesianCoordinateSystem` class.

### Changed
- API for `run_journal` function and `nxlib run` command to be more idiomatic, taking journal arguments as positional and all other arguments as keywords.

### Fixed
- Fixed issue where some parts couldn't be opened. Changed underlying open command from `SetNonmasterSeedPartData` to `OpenActiveDisplay`.
- Cleaned up type hints and docstrings for `nxlib.geometry.Geometry.to_nx` method overloads.

## [0.5.0] - 2026-03-02

Initial public release of nxlib
