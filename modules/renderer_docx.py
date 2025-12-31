# modules/renderer_docx.py
"""
DOCX Renderer - Render documents using docxtpl.
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from docxtpl import DocxTemplate
from docx import Document
from docx.shared import RGBColor, Pt
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

from .plugin_loader import PluginPack
from .context_builder import ContextBuilder
from .rule_engine import RuleEngine, EvaluationTrace


# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def ensure_output_dir() -> Path:
    """Ensure the output directory exists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class DocxRenderer:
    """Renders DOCX documents from templates and context."""

    def __init__(self, plugin: PluginPack):
        self.plugin = plugin
        self.template_path = plugin.get_template_path()
        self.context_builder = ContextBuilder(plugin)
        self.rule_engine = RuleEngine(plugin)
        self.formatting = plugin.formatting

    def render(
        self,
        data: dict,
        output_path: Optional[Path] = None,
        apply_cell_colors: bool = True
    ) -> tuple[Path, list[EvaluationTrace]]:
        """
        Render a document from the template.

        Args:
            data: Input data dictionary.
            output_path: Optional custom output path.
            apply_cell_colors: Whether to apply cell background colors.

        Returns:
            tuple: (output_path, evaluation_traces)
        """
        # Build context
        context = self.context_builder.build_context(data)

        # Evaluate rules
        visibility, traces = self.rule_engine.evaluate_all_rules(data)

        # Filter context based on visibility
        context["_visibility"] = visibility
        context["_show_master_file"] = data.get("master_file") == 1

        # Get enabled services
        context["enabled_services"] = self.rule_engine.get_enabled_services(data)

        # Load and render template
        doc = DocxTemplate(str(self.template_path))
        doc.render(context)

        # Apply cell colors if requested
        if apply_cell_colors:
            self._apply_cell_colors(doc.docx, data)

        # Determine output path
        if output_path is None:
            output_path = self._generate_output_path(data)

        # Save document
        ensure_output_dir()
        doc.save(str(output_path))

        return output_path, traces

    def _generate_output_path(self, data: dict) -> Path:
        """Generate output file path based on config pattern."""
        config = self.plugin.config
        pattern = config.get("output", {}).get("filename_pattern", "output_{{ plugin_id }}.docx")

        # Simple pattern replacement
        filename = pattern
        filename = filename.replace("{{ entidad_cliente }}", str(data.get("entidad_cliente", "unknown")))
        filename = filename.replace("{{ anyo_ejercicio }}", str(data.get("anyo_ejercicio", "")))

        # Clean filename
        filename = "".join(c if c.isalnum() or c in "._- " else "_" for c in filename)

        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{timestamp}{ext}"

        return OUTPUT_DIR / filename

    def _apply_cell_colors(self, doc: Document, data: dict) -> None:
        """Apply background colors to table cells based on enum values."""
        enum_colors = self.formatting.get("enum_colors", {})

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text = cell.text.strip().lower()
                    self._apply_color_if_match(cell, text, enum_colors)

    def _apply_color_if_match(self, cell, text: str, enum_colors: dict) -> None:
        """Apply color to a cell if the text matches an enum value."""
        # Check compliance_color
        compliance_map = enum_colors.get("compliance_color", {}).get("values", {})
        if text in compliance_map:
            color_def = compliance_map[text]
            self._set_cell_background(cell, color_def.get("background", "#FFFFFF"))
            return

        # Check cumplido_color
        cumplido_map = enum_colors.get("cumplido_color", {}).get("values", {})
        if text in cumplido_map:
            color_def = cumplido_map[text]
            self._set_cell_background(cell, color_def.get("background", "#FFFFFF"))
            return

        # Check afectacion_color
        afectacion_map = enum_colors.get("afectacion_color", {}).get("values", {})
        if text in afectacion_map:
            color_def = afectacion_map[text]
            self._set_cell_background(cell, color_def.get("background", "#FFFFFF"))
            return

    def _set_cell_background(self, cell, hex_color: str) -> None:
        """Set the background color of a table cell."""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip("#")

            # Create shading element
            shading_elm = parse_xml(
                f'<w:shd {nsdecls("w")} w:fill="{hex_color}" w:val="clear"/>'
            )

            # Apply to cell
            cell._tc.get_or_add_tcPr().append(shading_elm)
        except Exception:
            pass  # Silently fail if color cannot be applied


def render_document(
    plugin: PluginPack,
    data: dict,
    output_path: Optional[Path] = None
) -> tuple[Path, list[EvaluationTrace]]:
    """
    Convenience function to render a document.

    Args:
        plugin: Loaded plugin pack.
        data: Input data dictionary.
        output_path: Optional custom output path.

    Returns:
        tuple: (output_path, evaluation_traces)
    """
    renderer = DocxRenderer(plugin)
    return renderer.render(data, output_path)
