import os
import uuid
from typing import Tuple

UPLOAD_DIR = os.path.join("uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload(file_bytes: bytes, filename: str, content_type: str) -> Tuple[str, str]:
    """
    Save uploaded bytes to disk in a safe, unique path.
    Returns (storage_path, stored_filename)
    """
    ext = os.path.splitext(filename)[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    storage_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(storage_path, "wb") as f:
        f.write(file_bytes)
    return storage_path, safe_name
