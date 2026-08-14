# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.8.0] - 2026-08-12

### Added
- Added the `nxlib.geometry.Geometry.transform` function, which allows transforming `Geometry` objects from a local to a global coordinate system.

### Updated
- `nxlib.nxopen.component.find_components_in_assembly_tree` now takes multiple part number arguments. This allows for faster searching of multiple components within a large tree, requiring only a single recursive trip through the assembly tree.

## [0.7.0] - 2026-08-10

### Added
- Added the `nxlib.nxopen.component.find_components_in_assembly_tree` function, which recurses through an assembly tree and finds all components matching a given part number.

## [0.6.2] - 2026-08-05

### Fixed
- `component_is_reference` no longer fails if the component's parent assembly is unloaded.
- Added uv.lock to repository.

## [0.6.1] - 2026-04-13

### Changed
- The `nxlib.nxopen.part.part_context` function signature was updated to allow more explicit control over what happens when exiting the context manager. The `close_when_true` argument still
works but raises a deprecation warning.

### Fixed
- Parts are properly closed when the `nxlib.nxopen.part.part_context` complete. Error messages such as `In non-interactive mode.  Export directory C:\Users\2343177_1 is deleted.` at the end of journal execution should not longer be present.
- Opening an assembly with `open_assembly=False` (default) explicitly sets the load options to only load the base part; the entire assembly was being opened previously.

## [0.6.0] - 2026-03-27

### Added
- Added the `nxlib.geometry.CartesianCoordinateSystem` class, which mirrors the `NXOpen.CartesianCoordinateSystem` class.

### Changed
- API for `run_journal` function and `nxlib run` command to be more idiomatic, taking journal arguments as positional and all other arguments as keywords.

### Fixed
- Fixed issue where some parts couldn't be opened. Changed underlying open command from `SetNonmasterSeedPartData` to `OpenActiveDisplay`.
- Cleaned up type hints and docstrings for `nxlib.geometry.Geometry.to_nx` method overloads.

## [0.5.0] - 2026-03-02

Initial public release of nxlib
