#!/usr/bin/env python3
"""
ReFrag AI - Digital Evidence Fragment & Dataset Generator
Generates realistic multi-class raw source files (JPEG, PNG, PDF, ZIP, TEXT)
and slices them into cluster-sized binary fragments (default 4096 bytes).
Stores raw files in ml/data/raw/<type>/, fragments in ml/data/fragments/,
and saves complete metadata indices to ml/data/.
"""

import os
import sys
import json
import csv
import zlib
import struct
import random
import hashlib
import argparse
from pathlib import Path

# Mapping file extensions and folder names to canonical types
CATEGORY_EXTENSIONS = {
    "jpeg": [".jpg", ".jpeg"],
    "png": [".png"],
    "pdf": [".pdf"],
    "zip": [".zip"],
    "text": [".txt", ".log", ".csv", ".json"],
}

EXTENSION_TO_CATEGORY = {}
for cat, exts in CATEGORY_EXTENSIONS.items():
    for ext in exts:
        EXTENSION_TO_CATEGORY[ext] = cat


def calculate_sha256(data: bytes) -> str:
    """Calculate SHA-256 hash of a byte sequence."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


# ==============================================================================
# SYNTHETIC DATA GENERATORS (Generating 20-50 realistic files per type)
# ==============================================================================

def create_synthetic_jpeg(file_path: Path, seed: int):
    """
    Creates an authentic JPEG file structure with SOI, APP0, DQT, SOF0, DHT,
    entropy-coded scan data, and EOI.
    """
    rng = random.Random(seed)
    width = rng.randint(400, 1920)
    height = rng.randint(300, 1080)

    # 1. SOI (Start of Image)
    soi = b"\xFF\xD8"

    # 2. APP0 (JFIF Header)
    app0 = (
        b"\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"
    )

    # 3. DQT (Define Quantization Table)
    dqt = b"\xFF\xDB\x00C\x00" + bytes([rng.randint(8, 64) for _ in range(64)])

    # 4. SOF0 (Start of Frame - Baseline DCT)
    # Length: 8 + 3*components = 17 bytes (0x0011)
    sof0 = (
        b"\xFF\xC0\x00\x11\x08"
        + struct.pack(">HH", height, width)
        + b"\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01"
    )

    # 5. DHT (Define Huffman Table)
    dht = b"\xFF\xC4\x00\x1F\x00" + bytes([rng.randint(0, 15) for _ in range(29)])

    # 6. SOS (Start of Scan)
    sos = b"\xFF\xDA\x00\x0C\x03\x01\x00\x02\x11\x03\x11\x00\x3F\x00"

    # 7. Entropy-coded payload (varied size between 12KB and 60KB)
    payload_len = rng.randint(12000, 60000)
    # Generate high-entropy bytes simulating DCT coefficients
    raw_payload = bytearray(rng.randbytes(payload_len))
    # In JPEG scans, 0xFF must be byte-stuffed with 0x00
    scan_data = bytearray()
    for b in raw_payload:
        scan_data.append(b)
        if b == 0xFF:
            scan_data.append(0x00)

    # 8. EOI (End of Image)
    eoi = b"\xFF\xD9"

    full_jpeg = soi + app0 + dqt + sof0 + dht + sos + bytes(scan_data) + eoi
    file_path.write_bytes(full_jpeg)


def create_synthetic_png(file_path: Path, seed: int):
    """
    Creates a valid PNG structure with signature, IHDR, tEXt, IDAT, and IEND.
    """
    rng = random.Random(seed)
    width = rng.randint(256, 1280)
    height = rng.randint(256, 1024)

    # 1. Signature
    sig = b"\x89PNG\r\n\x1a\n"

    # 2. IHDR Chunk (Length=13, Type=IHDR, Data, CRC)
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data))
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + ihdr_crc

    # 3. Optional tEXt Chunk
    comment = f"ReFrag-Forensics-Sample-{seed}".encode("ascii")
    text_data = b"Comment\x00" + comment
    text_crc = struct.pack(">I", zlib.crc32(b"tEXt" + text_data))
    text_chunk = struct.pack(">I", len(text_data)) + b"tEXt" + text_data + text_crc

    # 4. IDAT Chunks with zlib-compressed scanline data (14KB - 55KB)
    raw_img_size = rng.randint(14000, 55000)
    img_bytes = rng.randbytes(raw_img_size)
    compressed_idat = zlib.compress(img_bytes, level=rng.choice([1, 6, 9]))
    idat_crc = struct.pack(">I", zlib.crc32(b"IDAT" + compressed_idat))
    idat = struct.pack(">I", len(compressed_idat)) + b"IDAT" + compressed_idat + idat_crc

    # 5. IEND Chunk
    iend = b"\x00\x00\x00\x00IEND\xaeB`\x82"

    full_png = sig + ihdr + text_chunk + idat + iend
    file_path.write_bytes(full_png)


def create_synthetic_pdf(file_path: Path, seed: int):
    """
    Creates an authentic PDF file structure with header, catalog, pages,
    content streams, xref table, trailer, and %%EOF.
    """
    rng = random.Random(seed)
    num_pages = rng.randint(2, 8)
    pdf_version = rng.choice(["1.4", "1.5", "1.6", "1.7"])

    header = f"%PDF-{pdf_version}\n%âãÏÓ\n"

    # Varied body paragraphs
    forensic_phrases = [
        f"Case Evidence Investigation Report - Incident ID #RF-{seed:04d}.\n",
        "Storage media analysis: sector-level carving initiated on unallocated cluster blocks.\n",
        "Digital artifact recovery demonstrated structural integrity above 88% threshold.\n",
        "Forensic chain of custody maintained under cryptographic verification standards.\n",
        "Cryptographic hash sha256 validation confirmed identical block alignment.\n",
        "Reconstructed cluster sequences evaluated across relational compatibility matrices.\n",
    ]

    body_chunks = []
    offsets = []
    current_offset = len(header.encode("latin1"))

    # Object 1: Catalog
    obj1 = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    offsets.append(current_offset)
    body_chunks.append(obj1)
    current_offset += len(obj1.encode("latin1"))

    # Object 2: Pages
    kids = " ".join([f"{3 + i*2} 0 R" for i in range(num_pages)])
    obj2 = f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {num_pages} >>\nendobj\n"
    offsets.append(current_offset)
    body_chunks.append(obj2)
    current_offset += len(obj2.encode("latin1"))

    obj_num = 3
    for p in range(num_pages):
        content_stream = "".join(rng.choices(forensic_phrases, k=rng.randint(25, 60)))
        # Repeat to create realistic file size (12KB to 70KB)
        content_stream = content_stream * rng.randint(3, 8)
        stream_len = len(content_stream.encode("utf-8"))

        # Content Stream Object
        c_obj = (
            f"{obj_num + 1} 0 obj\n<< /Length {stream_len} >>\nstream\n"
            f"{content_stream}\nendstream\nendobj\n"
        )
        content_offset = current_offset

        # Page Object
        page_obj = (
            f"{obj_num} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {obj_num + 1} 0 R >>\n"
            f"endobj\n"
        )

        offsets.append(current_offset)
        body_chunks.append(page_obj)
        current_offset += len(page_obj.encode("latin1"))

        offsets.append(current_offset)
        body_chunks.append(c_obj)
        current_offset += len(c_obj.encode("utf-8"))

        obj_num += 2

    total_objects = len(offsets) + 1
    xref_offset = current_offset

    # XREF Table
    xref = [f"xref\n0 {total_objects}\n0000000000 65535 f \n"]
    for off in offsets:
        xref.append(f"{off:010d} 00000 n \n")

    xref_str = "".join(xref)
    trailer = (
        f"trailer\n<< /Size {total_objects} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )

    full_pdf = header + "".join(body_chunks) + xref_str + trailer
    file_path.write_bytes(full_pdf.encode("utf-8", errors="replace"))


def create_synthetic_zip(file_path: Path, seed: int):
    """
    Creates an authentic multi-entry ZIP archive structure with
    Local File Headers, compressed payloads, Central Directory, and EOCD.
    """
    rng = random.Random(seed)
    num_files = rng.randint(3, 7)

    filenames = [
        f"evidence_log_{seed}_{i}.txt" if i % 2 == 0 else f"checksums_{seed}_{i}.dat"
        for i in range(num_files)
    ]

    local_headers = bytearray()
    cd_headers = bytearray()
    local_offsets = []

    for name in filenames:
        name_bytes = name.encode("utf-8")
        payload_len = rng.randint(3000, 14000)
        data = rng.randbytes(payload_len)
        compressed = zlib.compress(data, level=6)[2:-4]  # raw deflate stream
        crc = zlib.crc32(data)

        local_offsets.append(len(local_headers))

        # Local File Header
        lh = struct.pack(
            "<4sHHHHHIIIHH",
            b"PK\x03\x04",
            20,             # version needed
            0,              # general purpose bit flag
            8,              # compression (deflate)
            0x4B21, 0x5462, # mod time/date
            crc,
            len(compressed),
            len(data),
            len(name_bytes),
            0,              # extra field length
        )
        local_headers.extend(lh + name_bytes + compressed)

        # Central Directory Record
        cd = struct.pack(
            "<4sHHHHHHIIIHHHHHII",
            b"PK\x01\x02",
            20,             # version made by
            20,             # version needed
            0,              # flags
            8,              # compression
            0x4B21, 0x5462,
            crc,
            len(compressed),
            len(data),
            len(name_bytes),
            0, 0, 0, 0, 0,
            local_offsets[-1],
        )
        cd_headers.extend(cd + name_bytes)

    cd_offset = len(local_headers)
    cd_size = len(cd_headers)

    # End of Central Directory Record
    eocd = struct.pack(
        "<4sHHHHIIH",
        b"PK\x05\x06",
        0, 0,
        len(filenames),
        len(filenames),
        cd_size,
        cd_offset,
        0,
    )

    full_zip = bytes(local_headers + cd_headers + eocd)
    file_path.write_bytes(full_zip)


def create_synthetic_text(file_path: Path, seed: int):
    """
    Creates structured text datasets: syslog lines, CSV database records,
    or forensic audit JSON entries.
    """
    rng = random.Random(seed)
    ext = file_path.suffix.lower()
    line_count = rng.randint(180, 500)

    if ext == ".json":
        records = [
            {
                "event_id": f"EVT-{seed}-{i:05d}",
                "timestamp": f"2026-09-25T14:{i % 60:02d}:{(i * 3) % 60:02d}Z",
                "severity": rng.choice(["INFO", "WARNING", "CRITICAL", "AUDIT"]),
                "source_ip": f"10.0.{rng.randint(1, 50)}.{rng.randint(2, 250)}",
                "destination_port": rng.choice([22, 80, 443, 3306, 8080]),
                "action": rng.choice(["ALLOW", "BLOCK", "QUARANTINE", "FLAG_FRAGMENT"]),
                "details": f"Sector trace analysis node #{seed % 10} recorded unmapped block allocation.",
            }
            for i in range(line_count)
        ]
        content = json.dumps(records, indent=2)

    elif ext == ".csv":
        header = "record_id,timestamp,module,cluster_id,hash_prefix,integrity_score,verdict\n"
        lines = [header]
        for i in range(line_count):
            lines.append(
                f"REC-{seed:04d}-{i:04d},2026-09-25 12:{i % 60:02d}:00,CarverModule,{i * 8},"
                f"0x{rng.randint(0x100000, 0xFFFFFF):06x},{rng.uniform(0.70, 0.99):.3f},"
                f"{rng.choice(['VALID', 'PARTIAL', 'RECOVERABLE'])}\n"
            )
        content = "".join(lines)

    else:  # .log or .txt
        lines = []
        for i in range(line_count):
            ip = f"192.168.{rng.randint(1, 10)}.{rng.randint(1, 254)}"
            node = f"cluster-node-{rng.randint(1, 12)}"
            lines.append(
                f"2026-09-25 15:{i % 60:02d}:{(i * 7) % 60:02d}.{rng.randint(100, 999)} [AUTH] "
                f"User admin session authenticated from {ip} via {node}. "
                f"Forensic acquisition state: {rng.choice(['STREAMING', 'ACTIVE', 'COMPLETED'])}\n"
            )
        content = "".join(lines)

    file_path.write_text(content, encoding="utf-8")


def generate_varied_sample_dataset(raw_dir: Path, count_per_type: int = 25):
    """
    Populates raw/jpeg, raw/png, raw/pdf, raw/zip, and raw/text
    with count_per_type varied, realistic files each (total ~125 files).
    """
    print(f"[*] Generating {count_per_type} sample files per category in {raw_dir}...")

    generators = {
        "jpeg": (create_synthetic_jpeg, [".jpg", ".jpeg"]),
        "png": (create_synthetic_png, [".png"]),
        "pdf": (create_synthetic_pdf, [".pdf"]),
        "zip": (create_synthetic_zip, [".zip"]),
        "text": (create_synthetic_text, [".txt", ".log", ".csv", ".json"]),
    }

    total_created = 0
    for cat_name, (func, extensions) in generators.items():
        cat_dir = raw_dir / cat_name
        cat_dir.mkdir(parents=True, exist_ok=True)

        existing = [f for f in cat_dir.glob("*") if f.is_file() and not f.name.startswith(".")]
        if len(existing) >= count_per_type:
            print(f"  [i] {cat_name}: already has {len(existing)} files. Skipping generation.")
            total_created += len(existing)
            continue

        needed = count_per_type - len(existing)
        print(f"  [+] Creating {needed} {cat_name.upper()} files...")
        for i in range(1, needed + 1):
            seed = 1000 + i * 37 + (hash(cat_name) % 500)
            ext = random.choice(extensions)
            filename = f"sample_{cat_name}_{i:03d}{ext}"
            file_path = cat_dir / filename
            func(file_path, seed)
            total_created += 1

    print(f"[+] Multi-class sample dataset ready. Total source files: {total_created}\n")


# ==============================================================================
# FRAGMENT SLICING ENGINE
# ==============================================================================

def slice_file_to_fragments(
    file_path: Path,
    output_dir: Path,
    block_size: int = 4096,
    global_counter: int = 1,
) -> tuple[list[dict], int]:
    """
    Slices a source file into standard block_size chunks and saves .bin fragments.
    """
    ext = file_path.suffix.lower()
    parent_name = file_path.parent.name.lower()

    # Determine file type category
    file_type = EXTENSION_TO_CATEGORY.get(ext)
    if not file_type and parent_name in CATEGORY_EXTENSIONS:
        file_type = parent_name
    elif not file_type:
        file_type = "unknown"

    file_bytes = file_path.read_bytes()
    file_size = len(file_bytes)

    if file_size == 0:
        return [], global_counter

    num_fragments = (file_size + block_size - 1) // block_size
    fragments_meta = []

    for i in range(num_fragments):
        offset = i * block_size
        chunk = file_bytes[offset : offset + block_size]
        frag_id = f"FRAG_{global_counter:06d}"
        global_counter += 1

        is_header = (i == 0)
        is_footer = (i == num_fragments - 1)

        # Write binary fragment to ml/data/fragments/
        frag_filename = f"{frag_id}.bin"
        frag_path = output_dir / frag_filename
        frag_path.write_bytes(chunk)

        meta = {
            "fragment_id": frag_id,
            "fragment_file": frag_filename,
            "source_file": file_path.name,
            "source_category": file_type,
            "file_type": file_type,
            "extension": ext,
            "offset": offset,
            "size_bytes": len(chunk),
            "is_header": is_header,
            "is_footer": is_footer,
            "fragment_index": i,
            "total_fragments": num_fragments,
            "sha256": calculate_sha256(chunk),
        }
        fragments_meta.append(meta)

    return fragments_meta, global_counter


def main():
    parser = argparse.ArgumentParser(
        description="ReFrag AI - Digital Evidence Fragment Generator"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "data" / "raw"),
        help="Directory containing raw source files (default: ml/data/raw)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "data" / "fragments"),
        help="Directory to save raw binary fragments (default: ml/data/fragments)",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=4096,
        help="Fragment block size in bytes (e.g. 512, 1024, 2048, 4096). Default: 4096",
    )
    parser.add_argument(
        "--count-per-type",
        type=int,
        default=25,
        help="Number of synthetic files to generate per category if raw/ is empty (default: 25)",
    )
    parser.add_argument(
        "--generate-samples",
        action="store_true",
        help="Force generation of synthetic sample files",
    )

    args = parser.parse_args()

    raw_path = Path(args.input_dir)
    fragments_path = Path(args.output_dir)
    data_dir = fragments_path.parent

    raw_path.mkdir(parents=True, exist_ok=True)
    fragments_path.mkdir(parents=True, exist_ok=True)

    # Collect source files recursively
    source_files = [
        f for f in raw_path.rglob("*")
        if f.is_file() and not f.name.startswith(".")
    ]

    if not source_files or args.generate_samples:
        generate_varied_sample_dataset(raw_path, count_per_type=args.count_per_type)
        source_files = [
            f for f in raw_path.rglob("*")
            if f.is_file() and not f.name.startswith(".")
        ]

    print(f"[*] Slicing {len(source_files)} source files into {args.block_size}-byte fragments...")

    all_fragments = []
    counter = 1
    type_counts = {}

    for sf in sorted(source_files, key=lambda p: str(p)):
        metas, counter = slice_file_to_fragments(
            file_path=sf,
            output_dir=fragments_path,
            block_size=args.block_size,
            global_counter=counter,
        )
        all_fragments.extend(metas)
        cat = metas[0]["file_type"] if metas else "unknown"
        type_counts[cat] = type_counts.get(cat, 0) + len(metas)

    # Save metadata indices in ml/data/
    metadata_json_path = data_dir / "fragments_metadata.json"
    with open(metadata_json_path, "w", encoding="utf-8") as jf:
        json.dump(all_fragments, jf, indent=2)

    metadata_csv_path = data_dir / "fragments_metadata.csv"
    dataset_csv_path = data_dir / "dataset.csv"

    if all_fragments:
        fieldnames = list(all_fragments[0].keys())
        for target_csv in [metadata_csv_path, dataset_csv_path]:
            with open(target_csv, "w", newline="", encoding="utf-8") as cf:
                writer = csv.DictWriter(cf, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_fragments)

    print("\n[+] Fragment Slicing Complete!")
    print(f"  Total Source Files:     {len(source_files)}")
    print(f"  Total Fragments:        {len(all_fragments)}")
    print(f"  Binary Fragment Chunks: {fragments_path}")
    print(f"  Metadata (JSON):        {metadata_json_path}")
    print(f"  Metadata (CSV):         {metadata_csv_path}")
    print(f"  Dataset Index (CSV):    {dataset_csv_path}")
    print("  Fragment Breakdown by Category:")
    for cat, cnt in sorted(type_counts.items()):
        print(f"    - {cat.upper():10s}: {cnt:5d} fragments")


if __name__ == "__main__":
    main()
