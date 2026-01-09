# modules/word_text_extractor.py
"""
Word Text Extractor - Extract formatted text from Word document text library.

This module extracts comentarios valorativos from a Word document using
markers like {{COMENTARIO_TEXTO_i_START}} and {{COMENTARIO_TEXTO_i_END}}.

It preserves formatting (bold, italic, bullets) using docxtpl RichText.
"""
from pathlib import Path
from typing import Optional
from docx import Document
from docxtpl import RichText


# Path to the text library document
CONFIG_BASE = Path(__file__).parent.parent / "config"
TEXT_LIBRARY_PATH = CONFIG_BASE / "Text_comentario valorativo.docx"

# Number of comentarios valorativos (1-16)
NUM_COMENTARIOS = 16

# Cache for extracted texts (loaded once per session)
_cached_comentarios: Optional[dict] = None
_cached_plain_texts: Optional[dict] = None


def _has_bullet(para) -> bool:
    """Check if a paragraph has bullet/numbering."""
    return (
        para._element.pPr is not None
        and para._element.pPr.numPr is not None
    )


def _extract_paragraph_as_richtext(para, rt: RichText, is_first: bool = False) -> None:
    """
    Extract a paragraph and append it to RichText object.

    Args:
        para: python-docx Paragraph object.
        rt: RichText object to append to.
        is_first: If True, don't add paragraph break before.
    """
    # Add paragraph break if not first paragraph
    if not is_first:
        rt.add("\a")  # Paragraph break in Word

    # Add bullet prefix if paragraph has numbering
    if _has_bullet(para):
        rt.add("\t•\t")

    # Add runs with their formatting
    for run in para.runs:
        text = run.text
        if text:
            rt.add(
                text,
                bold=run.bold,
                italic=run.italic,
                underline=run.underline,
            )


def _extract_paragraph_as_plain_text(para) -> str:
    """
    Extract a paragraph as plain text with bullet prefix.

    Args:
        para: python-docx Paragraph object.

    Returns:
        Plain text string.
    """
    prefix = "• " if _has_bullet(para) else ""
    return prefix + para.text


def _load_comentarios_from_word() -> tuple[dict, dict]:
    """
    Load all comentarios from the Word text library.

    Returns:
        Tuple of (richtext_dict, plaintext_dict) where:
        - richtext_dict: {1: RichText, 2: RichText, ...}
        - plaintext_dict: {1: "plain text", 2: "plain text", ...}
    """
    if not TEXT_LIBRARY_PATH.exists():
        raise FileNotFoundError(f"Text library not found: {TEXT_LIBRARY_PATH}")

    doc = Document(str(TEXT_LIBRARY_PATH))

    richtext_results = {}
    plaintext_results = {}

    for i in range(1, NUM_COMENTARIOS + 1):
        start_marker = f"{{{{COMENTARIO_TEXTO_{i}_START}}}}"
        end_marker = f"{{{{COMENTARIO_TEXTO_{i}_END}}}}"

        in_section = False
        rt = RichText()
        plain_lines = []
        is_first = True

        for para in doc.paragraphs:
            text = para.text.strip()

            if start_marker in text:
                in_section = True
                continue

            if end_marker in text:
                in_section = False
                break

            if in_section and text:
                # Extract as RichText
                _extract_paragraph_as_richtext(para, rt, is_first)
                is_first = False

                # Extract as plain text
                plain_lines.append(_extract_paragraph_as_plain_text(para))

        richtext_results[i] = rt
        plaintext_results[i] = "\n".join(plain_lines)

    return richtext_results, plaintext_results


def get_comentarios_richtext() -> dict:
    """
    Get all comentarios as RichText objects for document generation.

    Uses caching - loads from Word only once per session.

    Returns:
        Dictionary mapping comentario index (1-16) to RichText object.
    """
    global _cached_comentarios, _cached_plain_texts

    if _cached_comentarios is None:
        _cached_comentarios, _cached_plain_texts = _load_comentarios_from_word()

    return _cached_comentarios


def get_comentarios_plain_text() -> dict:
    """
    Get all comentarios as plain text for UI preview.

    Uses caching - loads from Word only once per session.

    Returns:
        Dictionary mapping comentario index (1-16) to plain text string.
    """
    global _cached_comentarios, _cached_plain_texts

    if _cached_plain_texts is None:
        _cached_comentarios, _cached_plain_texts = _load_comentarios_from_word()

    return _cached_plain_texts


def get_comentario_richtext(index: int) -> RichText:
    """
    Get a single comentario as RichText.

    Args:
        index: Comentario index (1-16).

    Returns:
        RichText object for the comentario.
    """
    comentarios = get_comentarios_richtext()
    return comentarios.get(index, RichText())


def get_comentario_plain_text(index: int) -> str:
    """
    Get a single comentario as plain text.

    Args:
        index: Comentario index (1-16).

    Returns:
        Plain text string for the comentario.
    """
    texts = get_comentarios_plain_text()
    return texts.get(index, "")


def clear_cache() -> None:
    """Clear the cached comentarios (useful for testing or reloading)."""
    global _cached_comentarios, _cached_plain_texts
    _cached_comentarios = None
    _cached_plain_texts = None


def get_comentario_title(index: int) -> str:
    """
    Extract the title (first line) of a comentario for UI display.

    Args:
        index: Comentario index (1-16).

    Returns:
        First line of the comentario text, typically the title.
    """
    text = get_comentario_plain_text(index)
    if text:
        lines = text.strip().split("\n")
        if lines:
            return lines[0].strip()
    return f"Comentario {index}"
