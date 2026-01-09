# modules/comentarios_valorativos.py
"""
Comentarios Valorativos Module - Processing logic for conditional evaluative comments.

This module handles:
- Loading comentarios valorativos definitions from YAML (questions only)
- Extracting formatted text from Word document library
- Building text previews (first 3 lines) for UI display
- Building context data for document generation with RichText formatting
"""
from typing import Any
from docxtpl import RichText

from .word_text_extractor import (
    get_comentarios_plain_text,
    get_comentarios_richtext,
    get_comentario_plain_text,
    get_comentario_richtext,
    NUM_COMENTARIOS,
)


def get_text_preview(text: str, max_lines: int = 3) -> str:
    """
    Extract the first N lines of text for preview display.

    Args:
        text: The full text content.
        max_lines: Maximum number of lines to include in preview.

    Returns:
        The first N lines of text, with ellipsis if truncated.
    """
    if not text:
        return ""

    lines = text.strip().split('\n')
    preview_lines = lines[:max_lines]
    preview = '\n'.join(preview_lines)

    if len(lines) > max_lines:
        preview += "\n..."

    return preview


def get_comentarios_for_ui(comentarios_defs: dict) -> list[dict]:
    """
    Prepare comentarios valorativos data for UI rendering.

    Args:
        comentarios_defs: Dictionary of comentario definitions from YAML.

    Returns:
        List of dictionaries with UI-ready data:
        [
            {
                "id": "comentario_valorativo_1",
                "index": 1,
                "question": "...",
                "text_preview": "first 3 lines...",
                "full_text": "..."
            },
            ...
        ]
    """
    result = []

    # Get plain texts from Word document for preview
    plain_texts = get_comentarios_plain_text()

    for i in range(1, NUM_COMENTARIOS + 1):
        key = f"comentario_valorativo_{i}"
        comentario = comentarios_defs.get(key, {})

        question = comentario.get("question", f"[Pregunta {i} no definida]")

        # Get text from Word document
        full_text = plain_texts.get(i, "")
        text_preview = get_text_preview(full_text, max_lines=3)

        result.append({
            "id": key,
            "index": i,
            "question": question,
            "text_preview": text_preview,
            "full_text": full_text,
        })

    return result


def build_comentarios_context(data: dict, comentarios_defs: dict) -> dict:
    """
    Build context data for comentarios valorativos in document generation.

    This function:
    1. Checks each comentario_valorativo_i field value
    2. If "si", includes the corresponding RichText in the context
    3. Builds a list of selected comentarios for template iteration

    Args:
        data: Input data with comentario_valorativo_i field values.
        comentarios_defs: Dictionary of comentario definitions from YAML.

    Returns:
        Dictionary with:
        - comentarios_valorativos_selected: list of selected comentarios with text
        - comentario_texto_i: RichText for each comentario (empty if not selected)
    """
    context = {}
    selected = []

    # Get RichText objects from Word document
    richtext_dict = get_comentarios_richtext()
    plain_texts = get_comentarios_plain_text()

    for i in range(1, NUM_COMENTARIOS + 1):
        field_name = f"comentario_valorativo_{i}"
        texto_field_name = f"comentario_texto_{i}"

        value = data.get(field_name, "no")

        if value == "si":
            # Include the RichText in context for document generation
            context[texto_field_name] = richtext_dict.get(i, RichText())
            selected.append({
                "index": i,
                "id": field_name,
                "text": plain_texts.get(i, ""),  # Plain text for reference
            })
        else:
            # Empty RichText for non-selected
            context[texto_field_name] = RichText()

    context["comentarios_valorativos_selected"] = selected
    context["has_comentarios_valorativos"] = len(selected) > 0

    return context
