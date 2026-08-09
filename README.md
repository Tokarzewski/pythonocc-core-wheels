# pythonocc-core-wheels

**Unofficial**, pip-installable Linux wheels for [pythonocc-core](https://github.com/tpaviot/pythonocc-core), repackaged from the upstream [conda-forge](https://github.com/conda-forge/pythonocc-core-feedstock) binary.

Not affiliated with, endorsed by, or supported by the pythonocc-core or OpenCASCADE (OCCT) maintainers. If you can use conda, **use conda-forge directly** — that is the maintainer-supported distribution channel and this project exists only to serve environments where conda isn't an option.

## Why this exists

`pythonocc-core` has no PyPI wheels; the only supported install path is conda-forge, because pythonocc-core wraps OpenCASCADE (OCCT), a large C++ CAD kernel that must be compiled and doesn't fit pip's normal "just compile the extension" model. This project doesn't recompile OCCT — it takes the **already-built, already-tested conda-forge binary** and repackages it into a standard manylinux wheel using `auditwheel`, so it can be `pip install`ed in environments without conda.

## Status

**Experimental, Linux-only, unpublished.** Nothing is on PyPI yet. The build pipeline in `.github/workflows/build-wheel.yml` produces a downloadable CI artifact per Python version so the approach can be validated before committing to a PyPI release.

Done:
- [x] Confirmed the wheel actually imports and runs `OCC.Core.*` calls correctly on a clean machine (no conda on PATH, a plain venv) — smoke-tested in CI with a real `OCC.Core.BRepPrimAPI_MakeBox(...).Shape()` call.
- [x] `numpy` declared as a runtime dependency (several `OCC.Core` SWIG modules need it at import time).
- [x] Wheel is correctly tagged `cpXY-cpXY-manylinux_...` (not `py3-none-any`) — the raw build bundles a specific-CPython-ABI native extension, so it needs `setup.py`'s `Distribution.has_ext_modules() = True` override to get setuptools to tag it as version/ABI-specific rather than falsely claiming universal Python 3 compatibility.
- [x] Multiple Python versions: 3.10–3.14, matching conda-forge's own `pythonocc-core-feedstock` support matrix, built in parallel matrix jobs.

Not yet done / to validate:
- [ ] Confirm wheel size is reasonable (only `OCC.Core` is packaged; `OCC.Display`/`OCC.Extend`, which pull in VTK/Qt, are deliberately excluded).
- [ ] macOS and Windows builds.
- [ ] Actual PyPI publish (needs a registered project name + trusted publishing or API token).
- [ ] Whether any `OCC.Core` functionality beyond basic BRep calls needs OCCT's runtime resource files / `CSF_*` environment variables that conda's activation scripts normally set up (unverified beyond the smoke test's narrow coverage).

## Scope

Only the `OCC.Core` namespace is packaged (the geometry-kernel bindings). `OCC.Display` and other visualization-related submodules are intentionally dropped from the wheel to avoid pulling in their much heavier dependency chain (VTK, Qt, etc.), since typical downstream consumers only need `OCC.Core.*`.

## Known limitation: glibc/manylinux tag

The wheel is built on GitHub's `ubuntu-latest` runner and its actual required platform tag is determined empirically by `auditwheel` from the linked symbol versions, rather than pinned in advance — an earlier attempt to force `manylinux_2_28` failed outright because the runner's glibc/libstdc++ versions are newer than that baseline allows. In practice this currently resolves to `manylinux_2_39_x86_64`, meaning **installing systems need a fairly recent glibc** (roughly Ubuntu 24.04+ / Debian 13+ / Fedora 40+ era). Older distros are not supported by this wheel; building inside an actual manylinux Docker container (rather than directly on the runner) would lower this requirement, but hasn't been attempted yet.

## Licensing

The build scripts and CI configuration in this repository are MIT licensed (see `LICENSE`). The redistributed binaries themselves are pythonocc-core / OpenCASCADE (OCCT), both licensed under LGPL-2.1 (with the OCCT public-patent exception) — see the upstream projects for their full license terms. Redistributing these binaries is intended to remain within the terms of that license; this is not legal advice, and this repackaging effort has not been reviewed by a lawyer.
