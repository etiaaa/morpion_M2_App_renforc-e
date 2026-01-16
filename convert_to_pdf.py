#!/usr/bin/env python3
"""
Simple script to convert rapport_tp.md to PDF
"""
import fitz  # PyMuPDF
from markdown_it import MarkdownIt
from pathlib import Path

def markdown_to_pdf(md_file, pdf_file):
    """Convert Markdown file to PDF"""
    # Read markdown file
    md_content = Path(md_file).read_text(encoding='utf-8')

    # Parse markdown to get text (simplified)
    md = MarkdownIt()
    tokens = md.parse(md_content)

    # Create PDF
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    # Simple text rendering
    y_position = 50
    x_position = 50

    # Split by lines and render
    lines = md_content.split('\n')
    for line in lines:
        if y_position > 750:  # New page if needed
            page = doc.new_page(width=595, height=842)
            y_position = 50

        # Skip if line is too long (image references, etc.)
        if len(line) > 100:
            continue

        page.insert_text((x_position, y_position), line, fontsize=11)
        y_position += 15

    # Save PDF
    doc.save(pdf_file)
    doc.close()
    print(f"✅ PDF créé: {pdf_file}")

if __name__ == "__main__":
    markdown_to_pdf("rapport_tp.md", "rapport_tp.pdf")
