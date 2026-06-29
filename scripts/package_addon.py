from __future__ import annotations

import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDON_DIR = ROOT / "addon"
DIST_DIR = ROOT / "dist"
PACKAGE_PATH = DIST_DIR / "ankilens.ankiaddon"

EXCLUDED_NAMES = {
    ".DS_Store",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
}

EXCLUDED_DIRS = {
    "__pycache__",
}


def main() -> None:
    DIST_DIR.mkdir(exist_ok=True)
    if PACKAGE_PATH.exists():
        PACKAGE_PATH.unlink()
    files = sorted(path for path in ADDON_DIR.rglob("*") if _include(path))
    if not files:
        raise SystemExit("no add-on files found")
    with zipfile.ZipFile(PACKAGE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ADDON_DIR).as_posix())
    print(PACKAGE_PATH)


def _include(path: Path) -> bool:
    if not path.is_file():
        return False
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.name in EXCLUDED_NAMES:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


if __name__ == "__main__":
    main()
