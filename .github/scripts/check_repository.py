from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
MAINTAINED_DOCS = (
    "README.md",
    "CONTRIBUTING.md",
    "CLAUDE.md",
    "docs/README.md",
    "docs/getting_started.md",
    "docs/project_brief.md",
    "docs/review_guide.md",
    "docs/research_plan.md",
    "docs/research_status.md",
    "docs/team_contributions.md",
    "docs/archive/README.md",
    "experiments/README.md",
    "experiments/presentation/README.md",
    "SOTA/README.md",
    "legacy/README.md",
)


def prose_lines(content: str) -> list[str]:
    lines = []
    fence = None
    for line in content.splitlines():
        stripped = line.lstrip()
        if fence:
            if stripped.startswith(fence):
                fence = None
            continue
        match = re.match(r"(`{3,}|~{3,})", stripped)
        if match:
            fence = match.group(1)
        else:
            lines.append(line)
    return lines


def heading_ids(content: str) -> set[str]:
    identifiers = set()
    counts = {}
    for line in prose_lines(content):
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if not match:
            continue
        heading = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", match.group(1))
        heading = re.sub(r"<[^>]*>", "", heading).replace("`", "").replace("*", "")
        slug = "".join(
            character
            for character in heading.lower()
            if character in "-_ " or unicodedata.category(character)[0] in "LNM"
        ).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        identifiers.add(slug if count == 0 else f"{slug}-{count}")
    return identifiers


def check_links(path: Path) -> list[str]:
    errors = []
    content = "\n".join(prose_lines(path.read_text(encoding="utf-8")))
    for destination in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", content):
        parsed = urlsplit(destination)
        if parsed.scheme or destination.startswith("//"):
            continue
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        if not target.exists():
            errors.append(f"missing target: {destination}")
        elif parsed.fragment and target.suffix == ".md":
            if unquote(parsed.fragment) not in heading_ids(target.read_text(encoding="utf-8")):
                errors.append(f"missing heading: {destination}")
    return errors


def check_notebook(notebook: object) -> None:
    if not isinstance(notebook, dict) or notebook.get("nbformat") != 4:
        raise ValueError("expected a version 4 notebook")
    if not isinstance(notebook.get("metadata"), dict) or not isinstance(notebook.get("cells"), list):
        raise ValueError("expected notebook metadata and cells")
    for position, cell in enumerate(notebook["cells"]):
        if not isinstance(cell, dict) or cell.get("cell_type") not in {"code", "markdown", "raw"}:
            raise ValueError(f"invalid cell type at position {position}")
        source = cell.get("source")
        if not isinstance(source, str) and not (
            isinstance(source, list) and all(isinstance(line, str) for line in source)
        ):
            raise ValueError(f"invalid cell source at position {position}")


def main() -> int:
    errors = []
    for name in MAINTAINED_DOCS:
        try:
            errors.extend(f"{name}: {error}" for error in check_links(ROOT / name))
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f"{name}: {error}")

    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "experiments", "SOTA", "prompt", "legacy/src", "legacy/app.py", "legacy/railway.json"],
        cwd=ROOT,
    ).decode("utf-8").split("\0")
    names = sorted({name for name in tracked if name} | {".github/scripts/check_repository.py"})
    counts = {".py": 0, ".ipynb": 0, ".json": 0}
    for name in names:
        path = ROOT / name
        if path.suffix not in counts:
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if path.suffix == ".py":
                ast.parse(content, filename=name, feature_version=(3, 10))
            else:
                document = json.loads(content)
                if path.suffix == ".ipynb":
                    check_notebook(document)
            counts[path.suffix] += 1
        except (OSError, UnicodeError, ValueError, SyntaxError) as error:
            errors.append(f"{name}: {error}")

    if errors:
        print("Repository checks failed:")
        print("\n".join(errors))
        return 1
    print(
        f"Checked {len(MAINTAINED_DOCS)} documentation files, "
        f"{counts['.py']} Python files, {counts['.ipynb']} notebooks, "
        f"and {counts['.json']} JSON files. No experiments were executed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
