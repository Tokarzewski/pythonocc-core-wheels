# pythonocc-core-wheels

**Unofficial**, pip-installable wheels for [pythonocc-core](https://github.com/tpaviot/pythonocc-core), repackaged from the upstream [conda-forge](https://github.com/conda-forge/pythonocc-core-feedstock) binary, across Linux, macOS, and Windows.

Not affiliated with, endorsed by, or supported by the pythonocc-core or OpenCASCADE (OCCT) maintainers. If you can use conda, **use conda-forge directly** — that is the maintainer-supported distribution channel and this project exists only to serve environments where conda isn't an option.

## Why this exists

`pythonocc-core` has no PyPI wheels; the only supported install path is conda-forge, because pythonocc-core wraps OpenCASCADE (OCCT), a large C++ CAD kernel that must be compiled and doesn't fit pip's normal "just compile the extension" model. This project doesn't recompile OCCT — it takes the **already-built, already-tested conda-forge binary** and repackages it into a standard wheel using the platform-appropriate repair tool (`auditwheel` on Linux, `delocate` on macOS, `delvewheel` on Windows), so it can be `pip install`ed in environments without conda.

## Status

**Experimental, unpublished.** Nothing is on PyPI yet. The build pipeline in `.github/workflows/build-wheel.yml` runs a matrix of Python 3.10–3.14 across Linux, macOS, and Windows, producing a downloadable CI artifact per (OS, Python version) combination so the approach can be validated before committing to a PyPI release.

Done:
- [x] Confirmed the wheel actually imports and runs `OCC.Core.*` calls correctly on a clean machine (no conda on PATH, a plain venv) — smoke-tested in CI with a real `OCC.Core.BRepPrimAPI_MakeBox(...).Shape()` call, on each OS with its own repair tool's output.
- [x] Full namespace (`OCC.Display`, `OCC.Extend`, `OCC.Wrapper`) packaged and smoke-tested in the clean venv alongside `OCC.Core`.
- [x] `numpy` declared as a runtime dependency (several `OCC.Core` SWIG modules need it at import time).
- [x] Wheel is correctly tagged `cpXY-cpXY-<platform>` (not `py3-none-any`) — the raw build bundles a specific-CPython-ABI native extension, so it needs `setup.py`'s `Distribution.has_ext_modules() = True` override to get setuptools to tag it as version/ABI-specific rather than falsely claiming universal Python 3 compatibility.
- [x] Multiple Python versions: 3.10–3.14, matching conda-forge's own `pythonocc-core-feedstock` support matrix, built in parallel matrix jobs.
- [x] Cross-platform matrix: Linux (`auditwheel`), macOS (`delocate`), Windows (`delvewheel`) — each using the packaging ecosystem's standard tool for bundling a wheel's native shared-library dependencies on that OS.
- [x] VTK/Qt risk assessed and cleared (see "VTK/Qt verdict" below): the conda-forge `all` variant installs VTK as a conda dependency, but **no compiled pythonocc binding ever links a VTK or Qt library** — verified on Windows by `delvewheel` (zero Qt/VTK DLLs among the 71 vendored) and on linux-64 by inspecting the ELF `DT_NEEDED` entries of all 312 `OCC/Core/*.so` files (zero Qt/VTK, only OCCT `libTK*` + system libs). `OCC.Display`'s Qt/wx backends are pure-Python and lazily imported per `OCC.Display.backend`, so nothing needs vendoring in the first place.
- [x] Size check (Windows / Python 3.13 cell, built locally): repaired wheel is **88.7 MB** (347.7 MB uncompressed), well under PyPI's 200 MB/file limit, and the clean-venv smoke test (Core BRep + Display + Extend + Wrapper imports) passes with **no VTK/Qt installed** in the venv.

Not yet done / to validate:
- [ ] Re-verify the size + smoke-test across the *remaining* matrix cells via CI (Linux/macOS × py3.10–3.14); the Linux ELF analysis above was done on the upstream conda package, not on a repaired wheel.
- [ ] Confirm `auditwheel`/`delocate` bundle the full transitive closure of the OCCT `libTK*` libs (e.g. freetype/fontconfig pulled in via `TKOpenGl`) on the non-Windows runners — delvewheel already does this correctly on Windows.
- [ ] An actual first publish to PyPI (the `publish` job and PyPI Trusted Publisher config are wired up; nothing has been published yet — see "Releasing" below).
- [ ] Whether any `OCC.Core` functionality beyond basic BRep calls needs OCCT's runtime resource files / `CSF_*` environment variables that conda's activation scripts normally set up (unverified beyond the smoke test's narrow coverage).
- [ ] Whether conda-forge actually publishes every (OS, Python version) combination in the matrix — some cells may simply not exist upstream and fail cleanly at the `conda install` step rather than indicating a bug in this repo.

## Releasing

Publishing to PyPI happens only on an explicit GitHub Release (never on a plain push or PR, even though those still run the full build/test matrix). Authentication uses [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) — no token is stored anywhere in this repo. The `publish` job in `.github/workflows/build-wheel.yml` runs in the `pypi` GitHub Environment and requires a pending publisher already configured on PyPI (Account settings → Publishing) pointing at this repo, the `build-wheel.yml` workflow, and the `pypi` environment.

To cut a release: create a GitHub Release (with a matching tag, e.g. `v7.9.3`). That triggers the full 15-cell build matrix plus the `publish` job, which collects every matrix cell's wheel artifact and uploads all of them to PyPI in one pass.

## Scope

The **entire pythonocc namespace** is packaged, not just `OCC.Core`: `OCC.Core` (the compiled geometry/visualization kernel bindings), `OCC.Display` (the `OCCViewer` rendering layer), `OCC.Extend` (high-level helpers such as `TopologyUtils` and `DataExchange`), and `OCC.Wrapper` (utility functions, renamed from the older `OCC.Utils` in 7.9.x). These are all shipped by the upstream conda-forge `pythonocc-core=7.9.3` package; the repackaging simply no longer strips the pure-Python `Display`/`Extend`/`Wrapper` namespaces.

`OCC.Display`'s GUI backends (PyQt5/PySide2/PyQt6/PySide6/wx/tk) are **optional and lazily imported** — the wheel does not hard-depend on any of them, and the core `OCC.Display.OCCViewer` renderer works through the compiled `OCC.Core.Visualization` backend without VTK/Qt installed. If you need an interactive window, install the Qt/wx binding of your choice alongside this wheel.

### VTK/Qt verdict

`conda install pythonocc-core=7.9.3` resolves to the `all` occt variant, which drags **VTK 9.x** into the conda env — but VTK is a dependency of the OCCT toolkit package, not of the pythonocc bindings. The compiled `OCC.Core.*` modules link only OCCT toolkits (`TK*`), FreeImage + image codecs, freetype, TBB/OpenEXR/zlib/zstd and the VC runtime; they link **no `vtk*.dll/.so` and no Qt library** (verified: `delvewheel` report on Windows; ELF `DT_NEEDED` scan of all 312 linux-64 `.so` files). Consequently the wheel vendors ~64 MB of OCCT + codec DLLs and *nothing* Qt- or VTK-related, no VTK/Qt wheel is expected from PyPI, and declaring neither as a dependency is correct. The 200 MB PyPI file limit has ~110 MB of headroom in the worst cell measured.

## Known limitation: glibc/manylinux tag

The wheel is built on GitHub's `ubuntu-latest` runner and its actual required platform tag is determined empirically by `auditwheel` from the linked symbol versions, rather than pinned in advance — an earlier attempt to force `manylinux_2_28` failed outright because the runner's glibc/libstdc++ versions are newer than that baseline allows. In practice this currently resolves to `manylinux_2_39_x86_64`, meaning **installing systems need a fairly recent glibc** (roughly Ubuntu 24.04+ / Debian 13+ / Fedora 40+ era). Older distros are not supported by this wheel; building inside an actual manylinux Docker container (rather than directly on the runner) would lower this requirement, but hasn't been attempted yet.

## Licensing

The build scripts and CI configuration in this repository are MIT licensed (see `LICENSE`). The redistributed binaries themselves are pythonocc-core / OpenCASCADE (OCCT), both licensed under LGPL-2.1 (with the OCCT public-patent exception) — see the upstream projects for their full license terms. Redistributing these binaries is intended to remain within the terms of that license; this is not legal advice, and this repackaging effort has not been reviewed by a lawyer.
