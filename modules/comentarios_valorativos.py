# modules/comentarios_valorativos.py
"""
Comentarios Valorativos Module - Processing logic for conditional evaluative comments.

This module handles:
- Loading comentarios valorativos definitions from YAML
- Extracting text previews (first 3 lines) for UI display
- Building context data for document generation
"""
from typing import Any


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

    for i in range(1, 18):
        key = f"comentario_valorativo_{i}"
        comentario = comentarios_defs.get(key, {})

        question = comentario.get("question", f"[Pregunta {i} no definida]")
        full_text = comentario.get("text", "")
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
    2. If "si", includes the corresponding text in the context
    3. Builds a list of selected comentarios for template iteration

    Args:
        data: Input data with comentario_valorativo_i field values.
        comentarios_defs: Dictionary of comentario definitions from YAML.

    Returns:
        Dictionary with:
        - comentarios_valorativos_selected: list of selected comentarios with text
        - comentario_valorativo_i_text: individual text for each selected comentario
    """
    context = {}
    selected = []

    for i in range(1, 18):
        field_name = f"comentario_valorativo_{i}"
        text_field_name = f"{field_name}_text"

        value = data.get(field_name, "no")
        comentario_def = comentarios_defs.get(field_name, {})
        full_text = comentario_def.get("text", "")

        if value == "si":
            # Include the text in context
            context[text_field_name] = full_text
            selected.append({
                "index": i,
                "id": field_name,
                "text": full_text,
            })
        else:
            # Empty text for non-selected
            context[text_field_name] = ""

    context["comentarios_valorativos_selected"] = selected
    context["has_comentarios_valorativos"] = len(selected) > 0

    return context
