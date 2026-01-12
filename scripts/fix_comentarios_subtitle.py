#!/usr/bin/env python3
"""
Script to add conditional logic around the "Comentarios valorativos" subtitle in the template.

This wraps the subtitle and all 16 comentario blocks with:
{% if has_comentarios_valorativos %}
...subtitle and comentarios...
{% endif %}

So when no comentario is selected, the entire section (including the subtitle) is hidden.
"""

import zipfile
import shutil
import os
import re
from pathlib import Path


def fix_comentarios_subtitle(template_path: str, output_path: str = None):
    """
    Add conditional wrapper around Comentarios valorativos section.

    Args:
        template_path: Path to the template docx file
        output_path: Path for the modified template (defaults to overwriting original)
    """
    if output_path is None:
        output_path = template_path

    # Create a temp directory for extraction
    temp_dir = Path(template_path).parent / "temp_docx_edit"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    try:
        # Extract the docx
        with zipfile.ZipFile(template_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Read the document.xml
        doc_xml_path = temp_dir / "word" / "document.xml"
        with open(doc_xml_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the "Comentarios valorativos" paragraph
        # Pattern: a paragraph ending with </w:t></w:r></w:p> where text is "Comentarios valorativos"
        # We need to insert {% if has_comentarios_valorativos %} before this paragraph

        # The subtitle paragraph looks like:
        # <w:p ...><w:pPr>...</w:pPr><w:r ...><w:rPr>...</w:rPr><w:t>Comentarios valorativos</w:t></w:r></w:p>

        # Find the start of the paragraph containing "Comentarios valorativos"
        subtitle_match = re.search(
            r'(<w:p[^>]*>[^<]*(?:<[^>]+>[^<]*)*<w:t>Comentarios valorativos</w:t></w:r></w:p>)',
            content
        )

        if not subtitle_match:
            print("ERROR: Could not find 'Comentarios valorativos' subtitle in template")
            return False

        # Find the actual paragraph start before the subtitle
        subtitle_pos = content.find('Comentarios valorativos')

        # Search backwards for <w:p  (paragraph start)
        para_start = content.rfind('<w:p ', 0, subtitle_pos)
        if para_start == -1:
            para_start = content.rfind('<w:p>', 0, subtitle_pos)

        if para_start == -1:
            print("ERROR: Could not find paragraph start for subtitle")
            return False

        # Find the last {% endif %} for comentario_valorativo_16
        # This is after {{ comentario_texto_16 }} and before the next content

        # First find comentario_valorativo_16 condition
        cv16_match = re.search(r'comentario_valorativo_16\s*==\s*["\']si["\']', content)
        if not cv16_match:
            print("ERROR: Could not find comentario_valorativo_16 condition")
            return False

        cv16_pos = cv16_match.end()

        # Find the corresponding {% endif %}
        # Look for "endif" after comentario_texto_16
        texto16_pos = content.find('comentario_texto_1', cv16_pos)
        if texto16_pos == -1:
            print("ERROR: Could not find comentario_texto_16")
            return False

        # Find {% endif %} after this position
        # Note: In Word XML, "endif" may be split across multiple <w:t> elements
        # with spell-check markers, so we search for just "endif" in <w:t> tags
        endif_pattern = re.compile(r'<w:t[^>]*>endif</w:t>', re.IGNORECASE)

        # Find all endif positions after texto16
        endif_matches = list(endif_pattern.finditer(content, texto16_pos))

        if not endif_matches:
            print("ERROR: Could not find endif after comentario_texto_16")
            return False

        # The first endif after comentario_texto_16 is the one we want
        last_cv_endif = endif_matches[0]

        # Find the end of the paragraph containing this endif
        endif_end_pos = last_cv_endif.end()
        para_end = content.find('</w:p>', endif_end_pos)
        if para_end == -1:
            print("ERROR: Could not find paragraph end after last endif")
            return False
        para_end += len('</w:p>')

        # Now we need to:
        # 1. Insert {% if has_comentarios_valorativos %} before the subtitle paragraph
        # 2. Insert {% endif %} after the last comentario endif paragraph

        # Create the conditional wrapper paragraphs
        if_start = '<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:ind w:left="0"/></w:pPr><w:r><w:t>{% if has_comentarios_valorativos %}</w:t></w:r></w:p>'
        if_end = '<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:ind w:left="0"/></w:pPr><w:r><w:t>{% endif %}</w:t></w:r></w:p>'

        # Check if the conditional already exists
        if 'has_comentarios_valorativos' in content:
            print("WARNING: has_comentarios_valorativos already exists in template - skipping modification")
            return True

        # Build the new content
        new_content = (
            content[:para_start] +
            if_start +
            content[para_start:para_end] +
            if_end +
            content[para_end:]
        )

        # Write the modified document.xml
        with open(doc_xml_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Re-create the docx file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        print(f"SUCCESS: Template updated at {output_path}")
        print(f"  - Added '{{%% if has_comentarios_valorativos %%}}' before 'Comentarios valorativos' subtitle")
        print(f"  - Added '{{%% endif %%}}' after last comentario block")
        return True

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import sys

    template_path = sys.argv[1] if len(sys.argv) > 1 else "config/template_final.docx"
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    success = fix_comentarios_subtitle(template_path, output_path)
    sys.exit(0 if success else 1)
