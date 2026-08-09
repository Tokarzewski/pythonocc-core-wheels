# pythonocc-core-wheels

**Unofficial**, pip-installable Linux wheels for [pythonocc-core](https://github.com/tpaviot/pythonocc-core), repackaged from the upstream [conda-forge](https://github.com/conda-forge/pythonocc-core-feedstock) binary.

Not affiliated with, endorsed by, or supported by the pythonocc-core or OpenCASCADE (OCCT) maintainers. If you can use conda, **use conda-forge directly** — that is the maintainer-supported distribution channel and this project exists only to serve environments where conda isn't an option.

## Why this exists

`pythonocc-core` has no PyPI wheels; the only supported install path is conda-forge, because pythonocc-core wraps OpenCASCADE (OCCT), a large C++ CAD kernel that must be compiled and doesn't fit pip's normal "just compile the extension" model. This project doesn't recompile OCCT — it takes the **already-built, already-tested conda-forge binary** and repackages it into a standard manylinux wheel using `auditwheel`, so it can be `pip install`ed in environments without conda.

## Status

**Experimental, Linux-only, single Python version, unpublished.** Nothing is on PyPI yet. This is the first iteration of the build pipeline, wired up in `.github/workflows/build-wheel.yml`, producing a downloadable CI artifact so the approach can be validated before committing to a PyPI release.

Not yet done / to validate:
- [ ] Confirm the wheel actually imports and runs `OCC.Core.*` calls correctly on a clean machine (no conda) — OCCT relies on some runtime resource files and `CSF_*` environment variables that conda's activation scripts normally set up; whether the specific `OCC.Core` submodules used by downstream consumers need them is unverified.
- [ ] Confirm wheel size is reasonable (only `OCC.Core` is packaged; `OCC.Display`/`OCC.Extend`, which pull in VTK/Qt, are deliberately excluded).
- [ ] macOS and Windows builds.
- [ ] Multiple Python versions.
- [ ] Actual PyPI publish (needs a registered project name + trusted publishing or API token).

## Scope

Only the `OCC.Core` namespace is packaged (the geometry-kernel bindings). `OCC.Display` and other visualization-related submodules are intentionally dropped from the wheel to avoid pulling in their much heavier dependency chain (VTK, Qt, etc.), since typical downstream consumers only need `OCC.Core.*`.

## Licensing

The build scripts and CI configuration in this repository are MIT licensed (see `LICENSE`). The redistributed binaries themselves are pythonocc-core / OpenCASCADE (OCCT), both licensed under LGPL-2.1 (with the OCCT public-patent exception) — see the upstream projects for their full license terms. Redistributing these binaries is intended to remain within the terms of that license; this is not legal advice, and this repackaging effort has not been reviewed by a lawyer.
