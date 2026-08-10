# pythonocc-core-wheels

**Unofficial**, pip-installable wheels for [pythonocc-core](https://github.com/tpaviot/pythonocc-core), repackaged from the upstream [conda-forge](https://github.com/conda-forge/pythonocc-core-feedstock) binary, across Linux, macOS, and Windows.

Not affiliated with, endorsed by, or supported by the pythonocc-core or OpenCASCADE (OCCT) maintainers. If you can use conda, **use conda-forge directly** — that is the maintainer-supported distribution channel and this project exists only to serve environments where conda isn't an option.

## Why this exists

`pythonocc-core` has no PyPI wheels; the only supported install path is conda-forge, because pythonocc-core wraps OpenCASCADE (OCCT), a large C++ CAD kernel that must be compiled and doesn't fit pip's normal "just compile the extension" model. This project doesn't recompile OCCT — it takes the **already-built, already-tested conda-forge binary** and repackages it into a standard wheel using the platform-appropriate repair tool (`auditwheel` on Linux, `delocate` on macOS, `delvewheel` on Windows), so it can be `pip install`ed in environments without conda.

## Status

**Experimental, unpublished.** Nothing is on PyPI yet. The build pipeline in `.github/workflows/build-wheel.yml` runs a matrix of Python 3.10–3.14 across Linux, macOS, and Windows, producing a downloadable CI artifact per (OS, Python version) combination so the approach can be validated before committing to a PyPI release.

Done:
- [x] Confirmed the wheel actually imports and runs `OCC.Core.*` calls correctly on a clean machine (no conda on PATH, a plain venv) — smoke-tested in CI with a real `OCC.Core.BRepPrimAPI_MakeBox(...).Shape()` call, on each OS with its own repair tool's output.
- [x] `numpy` declared as a runtime dependency (several `OCC.Core` SWIG modules need it at import time).
- [x] Wheel is correctly tagged `cpXY-cpXY-<platform>` (not `py3-none-any`) — the raw build bundles a specific-CPython-ABI native extension, so it needs `setup.py`'s `Distribution.has_ext_modules() = True` override to get setuptools to tag it as version/ABI-specific rather than falsely claiming universal Python 3 compatibility.
- [x] Multiple Python versions: 3.10–3.14, matching conda-forge's own `pythonocc-core-feedstock` support matrix, built in parallel matrix jobs.
- [x] Cross-platform matrix: Linux (`auditwheel`), macOS (`delocate`), Windows (`delvewheel`) — each using the packaging ecosystem's standard tool for bundling a wheel's native shared-library dependencies on that OS.

Done (cont'd):
- [x] Confirmed conda-forge publishes every (OS, Python version) combination in the matrix: all 15 cells (5 Python versions × 3 OSes) installed and built cleanly with no upstream gaps.
- [x] Wheels stripped of debug symbols (`auditwheel repair --strip` on Linux; manual `strip -S -x` on the bundled OCCT dylibs and staged `OCC/*.so` extension modules on macOS, since `delocate-wheel` has no equivalent flag) **and recompressed with LZMA** (repaired wheels are DEFLATE; LZMA cuts the Linux wheel from ~109 MB down to ~79 MB — verified installable end-to-end) so every cell fits under PyPI's 100 MB/file limit for new projects. Windows was already under; the unstripped Linux (~117 MB) and macOS (~103 MB) were both over and failed the first real publish attempt outright (see "Releasing" below). A `Check wheel size` CI step now fails the build early if any wheel is still over 100 MB, rather than only finding out at publish time.
- [x] macOS `delocate` repair fixed: GitHub's macos-latest `/usr/bin/otool` is a shim that resolves via `xcodebuild -find otool`, which the runner SIGKILLs ("Unexpected first line: Killed: 9"). The build now installs conda-forge's `cctools` (a real `otool`/`install_name_tool`) and puts it first on PATH so delocate never touches the broken shim.

Not yet done / to validate:
- [ ] An actual first successful publish to PyPI (the first real attempt failed on the size limit above; retrying now that stripping is wired in — see "Releasing" below).
- [ ] Whether any `OCC.Core` functionality beyond basic BRep calls needs OCCT's runtime resource files / `CSF_*` environment variables that conda's activation scripts normally set up (unverified beyond the smoke test's narrow coverage).

## Releasing

Publishing to PyPI happens only on an explicit GitHub Release (never on a plain push or PR, even though those still run the full build/test matrix). Authentication uses [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — no token is stored anywhere in this repo. The `publish` job in `.github/workflows/build-wheel.yml` runs in the `pypi` GitHub Environment and requires a pending publisher already configured on PyPI (Account settings → Publishing) pointing at this repo, the `build-wheel.yml` workflow, and the `pypi` environment.

To cut a release: create a GitHub Release (with a matching tag, e.g. `v7.9.3`). That triggers the full 15-cell build matrix plus the `publish` job, which collects every matrix cell's wheel artifact and uploads all of them to PyPI in one pass.

## Scope

Only the `OCC.Core` namespace is packaged (the geometry-kernel bindings). `OCC.Display` and other visualization-related submodules are intentionally dropped from the wheel to avoid pulling in their much heavier dependency chain (VTK, Qt, etc.), since typical downstream consumers only need `OCC.Core.*`.

## Known limitation: glibc/manylinux tag

The wheel is built on GitHub's `ubuntu-latest` runner and its actual required platform tag is determined empirically by `auditwheel` from the linked symbol versions, rather than pinned in advance — an earlier attempt to force `manylinux_2_28` failed outright because the runner's glibc/libstdc++ versions are newer than that baseline allows. In practice this currently resolves to `manylinux_2_39_x86_64`, meaning **installing systems need a fairly recent glibc** (roughly Ubuntu 24.04+ / Debian 13+ / Fedora 40+ era). Older distros are not supported by this wheel; building inside an actual manylinux Docker container (rather than directly on the runner) would lower this requirement, but hasn't been attempted yet.

## Licensing

The build scripts and CI configuration in this repository are MIT licensed (see `LICENSE`). The redistributed binaries themselves are pythonocc-core / OpenCASCADE (OCCT), both licensed under LGPL-2.1 (with the OCCT public-patent exception) — see the upstream projects for their full license terms. Redistributing these binaries is intended to remain within the terms of that license; this is not legal advice, and this repackaging effort has not been reviewed by a lawyer.
