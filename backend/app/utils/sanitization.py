import os
import re

def sanitize_filename(filename: str) -> str:
    """
    Strips directory components and dangerous characters from a filename.
    """
    if not filename:
        return "unnamed_artifact"
    
    # Strip path info
    clean_name = os.path.basename(filename.replace("\\", "/"))
    # Remove null bytes or control characters
    clean_name = re.sub(r'[\x00-\x1f\x7f]', '', clean_name)
    
    return clean_name or "unnamed_artifact"

def sanitize_relative_path(path: str, filename: str = None) -> str:
    """
    Sanitizes relative paths for folder uploads to prevent path traversal.
    E.g. "evidence/../logs/photo.jpg" -> "logs/photo.jpg"
    """
    if not path or path.strip() == "":
        return sanitize_filename(filename) if filename else "unnamed_artifact"

    # Normalize backslashes to forward slashes
    clean_path = path.replace("\\", "/")
    
    # Strip drive letters (e.g., C:/) or leading slashes
    clean_path = re.sub(r'^[a-zA-Z]:', '', clean_path)
    clean_path = clean_path.lstrip('/')
    
    # Remove path traversal tokens like '..'
    parts = [part for part in clean_path.split('/') if part and part != '..' and part != '.']
    
    sanitized = "/".join(parts)
    return sanitized if sanitized else (sanitize_filename(filename) if filename else "unnamed_artifact")

def get_file_extension(filename: str) -> str:
    """
    Extract file extension (e.g., '.jpg') safely.
    """
    if not filename:
        return ""
    _, ext = os.path.splitext(filename)
    return ext.lower()
