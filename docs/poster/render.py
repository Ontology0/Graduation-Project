from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import qrcode
import qrcode.image.svg


DIRECTORY = Path(__file__).resolve().parent
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
URL = "https://github.com/Ontology0/Graduation-Project"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an A1 poster from its HTML source.")
    parser.add_argument("--directory", type=Path, default=DIRECTORY / "v2")
    directory = parser.parse_args().directory.resolve()
    source = directory / "Alltology_A1_draft.html"
    pdf = directory / "Alltology_A1_draft.pdf"
    if not source.is_file():
        raise SystemExit(f"Poster source not found: {source}")
    if not CHROME.is_file() or not shutil.which("pdftoppm"):
        raise SystemExit("Google Chrome and pdftoppm are required.")
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    qr.add_data(URL)
    qr.make(fit=True)
    qr.make_image(image_factory=qrcode.image.svg.SvgPathImage).save(directory / "repository-qr.svg")
    with tempfile.TemporaryDirectory(prefix="alltology-poster-chrome-") as profile:
        options = [
            str(CHROME),
            "--headless=new",
            "--disable-gpu",
            "--disable-background-networking",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-sync",
            "--no-pdf-header-footer",
            "--allow-file-access-from-files",
            "--virtual-time-budget=1500",
            f"--user-data-dir={profile}",
        ]
        result = subprocess.run(
            [*options, "--dump-dom", source.as_uri()],
            check=True,
            capture_output=True,
            text=True,
        )
        if 'data-layout-errors="[]"' not in result.stdout:
            report = re.search(r'data-layout-errors="([^"]*)"', result.stdout)
            raise SystemExit(f"Poster layout check failed: {report.group(1) if report else 'not available'}")
        subprocess.run([*options, f"--print-to-pdf={pdf}", source.as_uri()], check=True, capture_output=True)
    subprocess.run(
        [
            "pdftoppm", "-singlefile", "-png", "-r", "300",
            "-scale-to-x", "7016", "-scale-to-y", "9933",
            str(pdf), str(directory / "Alltology_A1_300dpi"),
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "pdftoppm", "-singlefile", "-png", "-scale-to", "2000",
            str(pdf), str(directory / "Alltology_A1_preview"),
        ],
        check=True,
        capture_output=True,
    )
    print(f"Created {pdf}, Alltology_A1_300dpi.png, and Alltology_A1_preview.png")


if __name__ == "__main__":
    main()
