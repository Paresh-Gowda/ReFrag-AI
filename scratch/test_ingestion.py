import hashlib
import httpx

API_URL = "http://localhost:8000/api/forensics"

def run_tests():
    print("=== STARTING FORENSIC INGESTION PIPELINE TESTS ===")

    client = httpx.Client(timeout=10.0)

    # Test 1: Upload single JPEG file
    jpeg_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00" + b"A" * 100
    jpeg_hash = hashlib.sha256(jpeg_bytes).hexdigest()

    files1 = [("files", ("test_image.jpg", jpeg_bytes, "image/jpeg"))]
    data1 = {"relative_paths": "evidence/test_image.jpg", "case_name": "Test Single JPEG Case"}

    response = client.post(f"{API_URL}/upload", files=files1, data=data1)
    print(f"Test 1 (Single File Upload): Status {response.status_code}")
    assert response.status_code == 201, f"Failed: {response.text}"
    result1 = response.json()
    case_id_1 = result1["case_id"]
    artifact_1 = result1["artifacts"][0]
    print(f"  -> Case ID: {case_id_1}")
    print(f"  -> Artifact SHA-256: {artifact_1['sha256']}")
    print(f"  -> Magic Signature: {artifact_1['magic_signature']}")
    assert artifact_1["sha256"] == jpeg_hash, "SHA-256 hash mismatch!"
    assert artifact_1["relative_path"] == "evidence/test_image.jpg", "Relative path mismatch!"

    # Test 2: Upload folder structure (PNG, PDF, ZIP, TXT, Raw binary)
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 50
    pdf_bytes = b"%PDF-1.4\n%EOF\n" + b"PDF_DATA_" * 10
    zip_bytes = b"PK\x03\x04\x14\x00\x00\x00\x00\x00" + b"ZIP_HEADER_" * 5
    txt_bytes = b"Forensic Investigation Log File 2026\nSystem output normal."
    raw_bytes = b"\x4D\x5A\x90\x00\x03\x00\x00\x00" + b"\x00" * 50  # Executable / Raw binary

    folder_files = [
        ("files", ("image.png", png_bytes, "image/png")),
        ("files", ("doc.pdf", pdf_bytes, "application/pdf")),
        ("files", ("archive.zip", zip_bytes, "application/zip")),
        ("files", ("log.txt", txt_bytes, "text/plain")),
        ("files", ("sample.raw", raw_bytes, "application/octet-stream")),
    ]
    folder_data = {
        "relative_paths": [
            "case_01/images/image.png",
            "case_01/docs/doc.pdf",
            "case_01/archives/archive.zip",
            "case_01/logs/log.txt",
            "case_01/raw/sample.raw"
        ],
        "case_name": "Test Folder Upload Case"
    }

    response = client.post(f"{API_URL}/upload", files=folder_files, data=folder_data)
    print(f"Test 2 (Folder Upload): Status {response.status_code}")
    assert response.status_code == 201, f"Failed: {response.text}"
    result2 = response.json()
    print(f"  -> Ingested Files: {result2['files_uploaded']}")
    print(f"  -> Total Size: {result2['total_size']} bytes")
    assert result2["files_uploaded"] == 5

    # Verify signatures and relative paths
    for art in result2["artifacts"]:
        print(f"     File: {art['relative_path']} | Type: {art['mime_type']} | Sig: {art['magic_signature']}")

    # Test 3: Download artifact & verify exact byte retrieval
    art_id = result1["artifacts"][0]["artifact_id"]
    dl_resp = client.get(f"{API_URL}/artifacts/{art_id}/download")
    print(f"Test 3 (Artifact Download & Integrity Check): Status {dl_resp.status_code}")
    assert dl_resp.status_code == 200
    assert dl_resp.content == jpeg_bytes, "Downloaded bytes do not match original bytes!"
    assert dl_resp.headers.get("X-SHA256-Hash") == jpeg_hash
    print("  -> Downloaded exact byte content verified successfully!")

    # Test 4: Duplicate file detection
    dup_files = [("files", ("duplicate_photo.jpg", jpeg_bytes, "image/jpeg"))]
    dup_data = {"relative_paths": "evidence/duplicate_photo.jpg", "case_name": "Duplicate Test"}
    dup_resp = client.post(f"{API_URL}/upload", files=dup_files, data=dup_data)
    print(f"Test 4 (Duplicate Detection): Status {dup_resp.status_code}")
    assert dup_resp.status_code == 201
    dup_result = dup_resp.json()
    dup_art = dup_result["artifacts"][0]
    print(f"  -> Is Duplicate Flagged: {dup_art['is_duplicate']}")
    assert dup_art["is_duplicate"] == True, "Duplicate artifact was not properly flagged!"

    # Test 5: Path Traversal Sanitization
    path_trav_files = [("files", ("malicious.txt", b"secret data", "text/plain"))]
    path_trav_data = {"relative_paths": "../../etc/passwd/malicious.txt"}
    trav_resp = client.post(f"{API_URL}/upload", files=path_trav_files, data=path_trav_data)
    print(f"Test 5 (Path Traversal Protection): Status {trav_resp.status_code}")
    assert trav_resp.status_code == 201
    trav_art = trav_resp.json()["artifacts"][0]
    print(f"  -> Sanitized relative path: '{trav_art['relative_path']}'")
    assert "../" not in trav_art["relative_path"], "Path traversal token was not sanitized!"

    print("\n=== ALL 5 INGESTION INTEGRITY TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
