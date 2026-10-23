from pathlib import Path

from pypdf import PdfReader


class ExtractionError(Exception):
    """Raised when document text extraction fails."""


def extract_text_from_txt(file_path: Path) -> str:
    try:
        return file_path.read_text(
            encoding="utf-8",
        )
    except UnicodeDecodeError:
        try:
            return file_path.read_text(
                encoding="utf-8-sig",
            )
        except UnicodeDecodeError as exc:
            raise ExtractionError(
                "Unable to decode text file"
            ) from exc


def extract_text_from_pdf(file_path: Path) -> str:
    try:
        reader = PdfReader(file_path)

        page_text = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                page_text.append(text)

        return "\n\n".join(page_text)

    except Exception as exc:
        raise ExtractionError(
            "Unable to extract text from PDF"
        ) from exc


def extract_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    raise ExtractionError(
        f"Unsupported file type: {extension}"
    )