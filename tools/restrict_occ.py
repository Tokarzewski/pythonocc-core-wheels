#!/usr/bin/env python3
"""Restrict an OCC package to the transitive closure of a seed module list.

The full pythonocc-core ships ~312 OCC.Core SWIG modules. topologicpy's
pythonocc backend only imports ~28 of them, whose transitive import closure is
~78 modules (STEP import/export, IGES, DXF, graphics/AIS, meshing-extra, etc.
are NOT needed). Keeping only the closure shrinks the wheel below PyPI's
100 MB/file limit even with standard DEFLATE compression (PyPI rejects
LZMA-compressed wheels).

The closure is computed by following `import OCC.Core.X` / `from OCC.Core.X`
statements in each wrapper's .py file, so it stays correct across pythonocc
releases.

Usage:
    python tools/restrict_occ.py <path/to/OCC> <seed1> <seed2> ...
"""
import os
import re
import sys


_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+OCC\.Core\.([A-Za-z0-9_]+)",
    re.M,
)


def closure(occ_core_dir: str, seeds) -> set:
    required = set(seeds)
    queue = list(required)
    while queue:
        name = queue.pop()
        path = os.path.join(occ_core_dir, name + ".py")
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for dep in _IMPORT_RE.findall(text):
            if dep not in required:
                required.add(dep)
                queue.append(dep)
    return required


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    occ_dir = sys.argv[1]
    core_dir = os.path.join(occ_dir, "Core")
    if not os.path.isdir(core_dir):
        print(f"not an OCC package dir: {occ_dir!r} (missing Core/)", file=sys.stderr)
        return 2
    seeds = sys.argv[2:]
    required = closure(core_dir, seeds)

    removed = 0
    for name in sorted(os.listdir(core_dir)):
        base = name[:-3] if name.endswith(".py") else (
            name[1:-3] if name.startswith("_") and name.endswith(".so") else (
                name[:-4] if name.endswith(".pyi") else None
            )
        )
        if base is None:
            continue
        if base.startswith("_") or base in ("__init__",):
            # __init__.py and underscore-prefixed helper modules are always kept.
            continue
        if base not in required:
            for ext in (".py", ".so", ".pyi"):
                target = os.path.join(
                    core_dir,
                    f"_{base}{ext}" if ext == ".so" else f"{base}{ext}",
                )
                if os.path.exists(target):
                    os.remove(target)
                    removed += 1
    print(f"restricted {occ_dir!r}: kept {len(required)} modules, removed {removed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())