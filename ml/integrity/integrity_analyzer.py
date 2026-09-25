#!/usr/bin/env python3

"""
ReFrag AI - Integrity Analyzer

Validates reconstructed binary candidates using:
- File signatures
- Structural markers
- File size
- Basic format-specific checks
"""

from pathlib import Path
import argparse
import json


ML_DIR = Path(__file__).resolve().parent.parent

DEFAULT_INPUT = ML_DIR / "reconstructed"
DEFAULT_OUTPUT = ML_DIR / "integrity"

MIN_FILE_SIZE = 100


def detect_file_type(data):
    """Detect common file types using file signatures."""

    if data.startswith(b"\xFF\xD8\xFF"):
        return "jpeg"

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    if data.startswith(b"%PDF"):
        return "pdf"

    if data.startswith(b"PK\x03\x04"):
        return "zip"

    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "gif"

    return "unknown"


def validate_jpeg(data):
    """
    Basic JPEG structural validation.
    JPEG should begin with FF D8 and normally end with FF D9.
    """

    if not data.startswith(b"\xFF\xD8\xFF"):
        return False, "Invalid JPEG header"

    if data.endswith(b"\xFF\xD9"):
        return True, "Valid JPEG header and end marker"

    return False, "JPEG end marker missing"


def validate_png(data):
    """Basic PNG structural validation."""

    signature = b"\x89PNG\r\n\x1a\n"

    if not data.startswith(signature):
        return False, "Invalid PNG signature"

    if b"IEND" not in data:
        return False, "PNG IEND chunk missing"

    return True, "Valid PNG signature and IEND marker"


def validate_pdf(data):
    """Basic PDF structural validation."""

    if not data.startswith(b"%PDF"):
        return False, "Invalid PDF header"

    if b"%%EOF" in data:
        return True, "Valid PDF header and EOF marker"

    return False, "PDF EOF marker missing"


def validate_zip(data):
    """Basic ZIP structural validation."""

    if not data.startswith(b"PK\x03\x04"):
        return False, "Invalid ZIP header"

    if b"PK\x05\x06" in data or b"PK\x01\x02" in data:
        return True, "ZIP signature and archive structure detected"

    return False, "ZIP end/central-directory marker missing"


def validate_file(path):
    """Run integrity checks on one reconstructed file."""

    data = path.read_bytes()

    size = len(data)

    file_type = detect_file_type(data)

    if size < MIN_FILE_SIZE:
        return {
            "file": path.name,
            "file_type": file_type,
            "size": size,
            "status": "CORRUPTED",
            "integrity_score": 0.0,
            "message": "File is too small",
        }

    if file_type == "jpeg":
        valid, message = validate_jpeg(data)

    elif file_type == "png":
        valid, message = validate_png(data)

    elif file_type == "pdf":
        valid, message = validate_pdf(data)

    elif file_type == "zip":
        valid, message = validate_zip(data)

    else:
        valid = False
        message = "Unknown file signature"

    if valid:
        status = "VALID"
        integrity_score = 1.0
    elif file_type != "unknown":
        status = "PARTIAL"
        integrity_score = 0.5
    else:
        status = "CORRUPTED"
        integrity_score = 0.0

    return {
        "file": path.name,
        "file_type": file_type,
        "size": size,
        "status": status,
        "integrity_score": integrity_score,
        "message": message,
    }


def analyze_directory(input_dir, output_dir):

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = sorted(
        input_dir.glob("reconstructed_*.bin")
    )

    print()
    print("======================================")
    print("        ReFrag AI Integrity Analysis")
    print("======================================")
    print()

    print(f"Input directory : {input_dir}")
    print(f"Files detected  : {len(files)}")
    print()

    results = []

    for index, path in enumerate(files, start=1):

        result = validate_file(path)

        results.append(result)

        print(
            f"[{index:03d}/{len(files):03d}] "
            f"{path.name:<25} "
            f"{result['file_type']:<8} "
            f"{result['status']:<10} "
            f"{result['integrity_score']:.0%}"
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    valid_count = sum(
        r["status"] == "VALID"
        for r in results
    )

    partial_count = sum(
        r["status"] == "PARTIAL"
        for r in results
    )

    corrupted_count = sum(
        r["status"] == "CORRUPTED"
        for r in results
    )

    print()
    print("--------------------------------------")
    print("Integrity Summary")
    print("--------------------------------------")
    print(f"Total files : {len(results)}")
    print(f"Valid       : {valid_count}")
    print(f"Partial     : {partial_count}")
    print(f"Corrupted   : {corrupted_count}")
    print("--------------------------------------")

    # --------------------------------------------------
    # Save JSON
    # --------------------------------------------------

    json_path = output_dir / "integrity_results.json"

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
        )

    # --------------------------------------------------
    # Save CSV
    # --------------------------------------------------

    import csv

    csv_path = output_dir / "integrity_results.csv"

    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "file",
                "file_type",
                "size",
                "status",
                "integrity_score",
                "message",
            ],
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"JSON results: {json_path}")
    print(f"CSV results : {csv_path}")


def main():

    parser = argparse.ArgumentParser(
        description="ReFrag AI Integrity Analyzer"
    )

    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Directory containing reconstructed files",
    )

    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Directory for integrity results",
    )

    args = parser.parse_args()

    analyze_directory(
        args.input,
        args.output,
    )


if __name__ == "__main__":
    main()