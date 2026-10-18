from pathlib import Path
from uuid import uuid4

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
}


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def generate_storage_filename(
    original_filename: str,
) -> str:
    safe_name = secure_filename(original_filename)

    if not safe_name:
        raise ValueError("Invalid filename")

    extension = get_file_extension(safe_name)

    return f"{uuid4().hex}{extension}"


def save_uploaded_file(
    file: FileStorage,
    upload_folder: Path,
) -> tuple[str, Path]:
    storage_filename = generate_storage_filename(
        file.filename or ""
    )

    destination = upload_folder / storage_filename

    file.save(destination)

    return storage_filename, destination