#!/usr/bin/env python3
"""Recompress every wheel in the given directory (glob arg) with LZMA.

Auditwheel / delocate / delvewheel emit DEFLATE-compressed wheels. The OCCT
shared libraries and OCC/Core SWIG extension modules are binary and compress
far better with LZMA: on Linux this drops a repaired wheel from ~109 MB (over
PyPI's 100 MB/file limit) to ~79 MB. Python's stdlib zipfile reads LZMA wheels
(non-zipfile tooling may expect DEFLATE, but pip and the wheel ecosystem read
any supported zip compression method), and we verified the result installs and
imports end-to-end. The files are recompressed in place, keeping the canonical
wheel filename (so the build tag still parses).

Usage: python tools/recompress_wheel.py 'wheelhouse/*.whl'
"""
import glob
import os
import sys
import zipfile


def recompress(src: str) -> None:
    tmp = src + ".tmp"
    with zipfile.ZipFile(src, "r") as zf_in:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_LZMA, compresslevel=9) as zf_out:
            for info in zf_in.infolist():
                ni = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                ni.compress_type = zipfile.ZIP_LZMA
                ni.external_attr = info.external_attr
                ni.create_system = info.create_system
                zf_out.writestr(ni, zf_in.read(info.filename))
    os.replace(tmp, src)
    print(f"{src}: {os.path.getsize(src)} bytes")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    pattern = sys.argv[1]
    wheels = sorted(glob.glob(pattern))
    if not wheels:
        print(f"no wheels matched {pattern!r}", file=sys.stderr)
        return 1
    for wheel in wheels:
        recompress(wheel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
