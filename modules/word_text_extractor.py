# modules/word_text_extractor.py
"""
Word Text Extractor - Extract formatted text from Word document text library.

This module extracts comentarios valorativos from a Word document using
markers like {{COMENTARIO_TEXTO_i_START}} and {{COMENTARIO_TEXTO_i_END}}.

It preserves formatting using docxtpl Subdoc for full paragraph formatting
preservation (indentation, list numbering, paragraph spacing).
"""
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import Optional
from docx import Document
from docxtpl import DocxTemplate, RichText

# Subdoc requires docxcompose which may not always be available
try:
    from docxtpl.subdoc import Subdoc

    SUBDOC_AVAILABLE = True
except ImportError:
    Subdoc = None  # type: ignore
    SUBDOC_AVAILABLE = False


# Path to the text library document
CONFIG_BASE = Path(__file__).parent.parent / "config"
TEXT_LIBRARY_PATH = CONFIG_BASE / "Text_comentario valorativo.docx"

# Number of comentarios valorativos (1-16)
NUM_COMENTARIOS = 16

# Cache for extracted texts (loaded once per session)
_cached_comentarios: Optional[dict] = None
_cached_plain_texts: Optional[dict] = None
# Cache for paragraph elements (used to create Subdocs)
_cached_paragraphs: Optional[dict] = None
# Cache the source document for deep copying paragraph elements
_cached_source_doc: Optional[Document] = None


class NumberingType(Enum):
    """Types of paragraph numbering."""
    NONE = "none"
    BULLET = "bullet"
    DECIMAL = "decimal"


# Track list counters per numId for proper numbering
_list_counters: dict = {}


def _get_numbering_type(para, doc) -> NumberingType:
    """
    Determine the numbering type of a paragraph.

    Args:
        para: python-docx Paragraph object.
        doc: python-docx Document object (needed for numbering definitions).

    Returns:
        NumberingType enum value (NONE, BULLET, or DECIMAL).
    """
    # Check if paragraph has numbering properties
    if para._element.pPr is None or para._element.pPr.numPr is None:
        return NumberingType.NONE

    num_pr = para._element.pPr.numPr

    # Get numId (numbering definition ID)
    if num_pr.numId is None:
        return NumberingType.NONE

    num_id = num_pr.numId.val
    if num_id == 0:
        return NumberingType.NONE

    # Get indentation level (default to 0)
    ilvl = 0
    if num_pr.ilvl is not None:
        ilvl = num_pr.ilvl.val

    # Try to get numbering format from document's numbering part
    try:
        numbering_part = doc.part.numbering_part
        if numbering_part is None:
            return NumberingType.BULLET  # Default to bullet if no definitions

        # Access the numbering XML element
        numbering_elm = numbering_part._element

        # Find the abstract numbering definition
        # First, find the num element with matching numId
        num_elm = None
        for num in numbering_elm.findall(
            './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num'
        ):
            if num.get(
                '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numId'
            ) == str(num_id):
                num_elm = num
                break

        if num_elm is None:
            return NumberingType.BULLET

        # Get the abstractNumId
        abstract_num_id_elm = num_elm.find(
            './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}abstractNumId'
        )
        if abstract_num_id_elm is None:
            return NumberingType.BULLET

        abstract_num_id = abstract_num_id_elm.get(
            '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'
        )

        # Find the abstract numbering definition
        abstract_num = None
        for an in numbering_elm.findall(
            './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}abstractNum'
        ):
            if an.get(
                '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}abstractNumId'
            ) == abstract_num_id:
                abstract_num = an
                break

        if abstract_num is None:
            return NumberingType.BULLET

        # Find the level definition for our ilvl
        for lvl in abstract_num.findall(
            './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lvl'
        ):
            if lvl.get(
                '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl'
            ) == str(ilvl):
                # Get the numFmt element
                num_fmt = lvl.find(
                    './/{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numFmt'
                )
                if num_fmt is not None:
                    fmt_val = num_fmt.get(
                        '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val'
                    )
                    # Check if it's a decimal/numeric format
                    if fmt_val in ('decimal', 'decimalZero', 'upperRoman',
                                   'lowerRoman', 'upperLetter', 'lowerLetter',
                                   'ordinal', 'cardinalText', 'ordinalText'):
                        return NumberingType.DECIMAL
                    else:
                        return NumberingType.BULLET
                break

        return NumberingType.BULLET

    except Exception:
        # If anything goes wrong, default to bullet
        return NumberingType.BULLET


def _get_list_number(para, doc) -> int:
    """
    Get the list number for a decimal-numbered paragraph.

    Uses internal counters to track numbering across paragraphs.

    Args:
        para: python-docx Paragraph object.
        doc: python-docx Document object.

    Returns:
        The list number (1, 2, 3, etc.).
    """
    global _list_counters

    if para._element.pPr is None or para._element.pPr.numPr is None:
        return 1

    num_pr = para._element.pPr.numPr
    if num_pr.numId is None:
        return 1

    num_id = num_pr.numId.val
    ilvl = 0
    if num_pr.ilvl is not None:
        ilvl = num_pr.ilvl.val

    # Create a unique key for this numbering list and level
    key = (num_id, ilvl)

    # Increment and return the counter
    if key not in _list_counters:
        _list_counters[key] = 1
    else:
        _list_counters[key] += 1

    return _list_counters[key]


def _reset_list_counters() -> None:
    """Reset all list counters (call before processing a new document)."""
    global _list_counters
    _list_counters = {}


def _has_bullet(para) -> bool:
    """Check if a paragraph has bullet/numbering (legacy compatibility)."""
    return (
        para._element.pPr is not None
        and para._element.pPr.numPr is not None
    )


def _extract_paragraph_as_richtext(
    para,
    rt: RichText,
    doc,
    is_first: bool = False,
    num_type: NumberingType = None,
    list_num: Optional[int] = None,
) -> None:
    """
    Extract a paragraph and append it to RichText object.

    Args:
        para: python-docx Paragraph object.
        rt: RichText object to append to.
        doc: python-docx Document object (needed for numbering detection).
        is_first: If True, don't add paragraph break before.
        num_type: Pre-computed numbering type (if None, will be detected).
        list_num: Pre-computed list number for decimal lists.
    """
    # Add paragraph break if not first paragraph
    if not is_first:
        rt.add("\a")  # Paragraph break in Word

    # Get numbering type if not provided
    if num_type is None:
        num_type = _get_numbering_type(para, doc)

    # Add appropriate prefix based on numbering type
    if num_type == NumberingType.DECIMAL:
        # For decimal lists, use the provided or computed number
        if list_num is None:
            list_num = _get_list_number(para, doc)
        rt.add(f"\t{list_num}.\t")
    elif num_type == NumberingType.BULLET:
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


def _extract_paragraph_as_plain_text(
    para,
    num_type: NumberingType = None,
    list_num: Optional[int] = None,
) -> str:
    """
    Extract a paragraph as plain text with appropriate list prefix.

    Args:
        para: python-docx Paragraph object.
        num_type: Pre-computed numbering type.
        list_num: Pre-computed list number for decimal lists.

    Returns:
        Plain text string.
    """
    if num_type == NumberingType.DECIMAL:
        prefix = f"{list_num}. " if list_num else "1. "
    elif num_type == NumberingType.BULLET:
        prefix = "• "
    else:
        prefix = ""
    return prefix + para.text


def _load_comentarios_from_word() -> tuple[dict, dict, dict, Document]:
    """
    Load all comentarios from the Word text library.

    Returns:
        Tuple of (richtext_dict, plaintext_dict, paragraphs_dict, source_doc) where:
        - richtext_dict: {1: RichText, 2: RichText, ...}
        - plaintext_dict: {1: "plain text", 2: "plain text", ...}
        - paragraphs_dict: {1: [para1, para2, ...], 2: [...], ...} (paragraph objects)
        - source_doc: The source Document object for paragraph copying
    """
    if not TEXT_LIBRARY_PATH.exists():
        raise FileNotFoundError(f"Text library not found: {TEXT_LIBRARY_PATH}")

    doc = Document(str(TEXT_LIBRARY_PATH))

    richtext_results = {}
    plaintext_results = {}
    paragraphs_results = {}

    for i in range(1, NUM_COMENTARIOS + 1):
        start_marker = f"{{{{COMENTARIO_TEXTO_{i}_START}}}}"
        end_marker = f"{{{{COMENTARIO_TEXTO_{i}_END}}}}"

        # Reset list counters for each comentario section
        _reset_list_counters()

        in_section = False
        rt = RichText()
        plain_lines = []
        section_paragraphs = []
        is_first = True

        for para in doc.paragraphs:
            text = para.text.strip()

            if start_marker in text:
                in_section = True
                continue

            if end_marker in text:
                in_section = False
                break

            if in_section:
                # Store the paragraph object for Subdoc creation
                section_paragraphs.append(para)

                # Keep empty paragraphs to preserve line breaks
                # but still extract content from non-empty ones
                if text:
                    # Get numbering info once to avoid double-counting
                    num_type = _get_numbering_type(para, doc)
                    list_num = None
                    if num_type == NumberingType.DECIMAL:
                        list_num = _get_list_number(para, doc)

                    # Extract as RichText (with formatting and numbering)
                    _extract_paragraph_as_richtext(
                        para, rt, doc, is_first, num_type, list_num
                    )
                    # Extract as plain text
                    plain_lines.append(
                        _extract_paragraph_as_plain_text(para, num_type, list_num)
                    )

                    # Add extra line break after the first paragraph (title)
                    # to ensure visual separation from body text in RichText mode
                    if is_first:
                        rt.add("\a")  # Extra paragraph break after title
                        plain_lines.append("")  # Blank line in plain text
                else:
                    # Empty paragraph - add line break for spacing
                    if not is_first:
                        rt.add("\a")  # Paragraph break in Word
                    plain_lines.append("")

                is_first = False

        richtext_results[i] = rt
        plaintext_results[i] = "\n".join(plain_lines)
        paragraphs_results[i] = section_paragraphs

    return richtext_results, plaintext_results, paragraphs_results, doc


def _ensure_cache_loaded() -> None:
    """Ensure the comentarios cache is loaded."""
    global _cached_comentarios, _cached_plain_texts, _cached_paragraphs, _cached_source_doc

    if _cached_comentarios is None:
        (
            _cached_comentarios,
            _cached_plain_texts,
            _cached_paragraphs,
            _cached_source_doc,
        ) = _load_comentarios_from_word()


def get_comentarios_richtext() -> dict:
    """
    Get all comentarios as RichText objects for document generation.

    Uses caching - loads from Word only once per session.

    Returns:
        Dictionary mapping comentario index (1-16) to RichText object.
    """
    _ensure_cache_loaded()
    return _cached_comentarios


def get_comentarios_plain_text() -> dict:
    """
    Get all comentarios as plain text for UI preview.

    Uses caching - loads from Word only once per session.

    Returns:
        Dictionary mapping comentario index (1-16) to plain text string.
    """
    _ensure_cache_loaded()
    return _cached_plain_texts


def get_comentarios_paragraphs() -> dict:
    """
    Get all comentarios as lists of paragraph objects.

    Uses caching - loads from Word only once per session.

    Returns:
        Dictionary mapping comentario index (1-16) to list of paragraph objects.
    """
    _ensure_cache_loaded()
    return _cached_paragraphs


def _create_subdoc_from_paragraphs(
    tpl: DocxTemplate, paragraphs: list
) -> Subdoc:
    """
    Create a Subdoc containing the specified paragraphs with full formatting.

    This preserves all Word paragraph formatting including:
    - Paragraph indentation and spacing
    - List numbering (bullets, decimal)
    - Text formatting (bold, italic, underline)
    - Empty paragraphs for spacing

    The first paragraph (typically the title) gets additional spacing after
    to ensure visual separation from the body text.

    Args:
        tpl: DocxTemplate object to create the Subdoc from.
        paragraphs: List of python-docx Paragraph objects to copy.

    Returns:
        Subdoc object containing the copied paragraphs.
    """
    subdoc = tpl.new_subdoc()

    # Word XML namespace
    w_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

    for idx, para in enumerate(paragraphs):
        # Deep copy the paragraph XML element to preserve all formatting
        new_para = deepcopy(para._element)

        # Add spacing after the first paragraph (title) to separate from body
        if idx == 0 and para.text.strip():
            # Get or create paragraph properties
            pPr = new_para.find(f"{w_ns}pPr")
            if pPr is None:
                from lxml import etree
                pPr = etree.SubElement(new_para, f"{w_ns}pPr")
                # Insert pPr at the beginning of the paragraph
                new_para.insert(0, pPr)

            # Get or create spacing element
            spacing = pPr.find(f"{w_ns}spacing")
            if spacing is None:
                from lxml import etree
                spacing = etree.SubElement(pPr, f"{w_ns}spacing")

            # Set spacing after (200 twips = ~10pt, provides visual separation)
            spacing.set(f"{w_ns}after", "200")

        subdoc.subdocx.element.body.append(new_para)

    return subdoc


def create_comentarios_subdocs(tpl: DocxTemplate) -> Optional[dict]:
    """
    Create Subdoc objects for all comentarios.

    This function creates fresh Subdoc objects each time it's called,
    as Subdocs cannot be reused across different template renders.
    The underlying paragraph data is cached for performance.

    Args:
        tpl: DocxTemplate object to create Subdocs from.

    Returns:
        Dictionary mapping comentario index (1-16) to Subdoc object,
        or None if docxcompose is not available.
    """
    if not SUBDOC_AVAILABLE:
        # docxcompose not installed, cannot create Subdocs
        return None

    _ensure_cache_loaded()

    subdocs = {}
    for i in range(1, NUM_COMENTARIOS + 1):
        paragraphs = _cached_paragraphs.get(i, [])
        if paragraphs:
            subdocs[i] = _create_subdoc_from_paragraphs(tpl, paragraphs)
        else:
            # Empty Subdoc for comentarios with no content
            subdocs[i] = tpl.new_subdoc()

    return subdocs


def is_subdoc_available() -> bool:
    """Check if Subdoc functionality is available (docxcompose installed)."""
    return SUBDOC_AVAILABLE


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
    global _cached_comentarios, _cached_plain_texts, _cached_paragraphs, _cached_source_doc
    _cached_comentarios = None
    _cached_plain_texts = None
    _cached_paragraphs = None
    _cached_source_doc = None


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
