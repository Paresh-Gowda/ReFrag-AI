import os

# Known magic numbers map
MAGIC_SIGNATURES = [
    (b"\xFF\xD8\xFF", "JPEG Image", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "PNG Image", "image/png"),
    (b"%PDF", "PDF Document", "application/pdf"),
    (b"PK\x03\x04", "ZIP Archive", "application/zip"),
    (b"PK\x05\x06", "ZIP Archive (Empty)", "application/zip"),
    (b"PK\x07\x08", "ZIP Archive (Spanned)", "application/zip"),
    (b"Rar!\x1a\x07", "RAR Archive", "application/x-rar-compressed"),
    (b"\x1f\x8b", "GZIP Archive", "application/gzip"),
    (b"7z\xbc\xaf\x27\x1c", "7-Zip Archive", "application/x-7z-compressed"),
    (b"MZ", "Windows Executable / Raw Binary", "application/x-msdownload"),
    (b"\x7fELF", "ELF Binary", "application/x-executable"),
]

def detect_file_signature(content: bytes, provided_mime: str = None, filename: str = None) -> tuple[str, str]:
    """
    Inspects initial bytes of a file to detect its magic signature and MIME type.
    Does NOT reject unknown files.
    Returns: (magic_signature_description, resolved_mime_type)
    """
    if not content or len(content) == 0:
        return "EMPTY_FILE", "application/x-empty"

    header = content[:32]
    header_hex = " ".join(f"{b:02X}" for b in header[:8])

    # Check known byte signatures
    for sig_bytes, description, mime in MAGIC_SIGNATURES:
        if content.startswith(sig_bytes):
            return f"{header_hex} ({description})", mime

    # Check if text file (printable ASCII / UTF-8 text)
    try:
        sample = content[:1024]
        # Allow tab, newline, carriage return and printable characters
        if all(c in (9, 10, 13) or 32 <= c <= 126 or c > 127 for c in sample):
            return f"ASCII/UTF-8 Text ({header_hex})", "text/plain"
    except Exception:
        pass

    # Fallback for raw / unknown forensic binary evidence
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    mime_fallback = provided_mime or "application/octet-stream"
    signature_desc = f"Raw Forensic Bytes ({header_hex})" if header_hex else "Raw Forensic Data"

    return signature_desc, mime_fallback
