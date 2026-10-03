"""Check that the two published skill discovery paths contain identical files."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "skills"
MIRROR = ROOT / ".agents" / "skills"


def files_under(root: Path) -> dict[Path, bytes]:
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def main() -> int:
    canonical = files_under(CANONICAL)
    mirror = files_under(MIRROR)
    differences = sorted(path for path in canonical.keys() | mirror.keys() if canonical.get(path) != mirror.get(path))
    if differences:
        for path in differences:
            print(f"Skill mirror differs: {path}")
        return 1
    print(f"Skill mirrors match: {len(canonical)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
