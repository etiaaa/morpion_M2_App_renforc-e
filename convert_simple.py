#!/usr/bin/env python3
"""
Solution la plus simple: Markdown -> HTML standalone
Puis ouvre dans le navigateur et fais Ctrl+P -> Enregistrer en PDF
"""
import markdown
from pathlib import Path
import webbrowser
import os

def convert_md_to_html(md_file, html_file):
    """Convert Markdown to standalone HTML"""

    # Read markdown
    md_content = Path(md_file).read_text(encoding='utf-8')

    # Convert to HTML with extensions
    html_body = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'tables', 'toc', 'fenced_code']
    )

    # Create standalone HTML with professional styling
    html_complete = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport TP - Morpion Q-Learning</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2.5cm;
            }}
            body {{
                font-size: 10pt;
            }}
            h1 {{
                page-break-before: always;
            }}
            h1:first-of-type {{
                page-break-before: avoid;
            }}
            img {{
                max-width: 100%;
                page-break-inside: avoid;
            }}
            pre, code {{
                page-break-inside: avoid;
            }}
        }}

        body {{
            font-family: 'Segoe UI', 'Calibri', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #fff;
        }}

        h1 {{
            color: #2c3e50;
            font-size: 28pt;
            margin-top: 30px;
            margin-bottom: 20px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}

        h2 {{
            color: #34495e;
            font-size: 22pt;
            margin-top: 25px;
            margin-bottom: 15px;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 8px;
        }}

        h3 {{
            color: #555;
            font-size: 16pt;
            margin-top: 20px;
            margin-bottom: 12px;
        }}

        h4 {{
            color: #666;
            font-size: 14pt;
            margin-top: 18px;
            margin-bottom: 10px;
        }}

        p {{
            margin: 12px 0;
            text-align: justify;
        }}

        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10pt;
            color: #c7254e;
        }}

        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-left: 4px solid #3498db;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            margin: 20px 0;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
            color: #333;
            font-size: 9pt;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        table, th, td {{
            border: 1px solid #ddd;
        }}

        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 10px;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        tr:hover {{
            background-color: #f5f5f5;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        blockquote {{
            border-left: 5px solid #3498db;
            padding: 10px 20px;
            margin: 20px 0;
            background-color: #f0f7fb;
            color: #555;
            font-style: italic;
        }}

        ul, ol {{
            margin: 15px 0;
            padding-left: 40px;
        }}

        li {{
            margin: 8px 0;
        }}

        a {{
            color: #3498db;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}

        .toc {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            margin: 30px 0;
        }}

        .toc ul {{
            list-style-type: none;
            padding-left: 20px;
        }}

        strong {{
            color: #2c3e50;
        }}

        em {{
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    {html_body}

    <script>
        // Auto-print dialog (optional - comment out if not wanted)
        // window.onload = function() {{
        //     setTimeout(function() {{
        //         window.print();
        //     }}, 1000);
        // }};
    </script>
</body>
</html>
"""

    # Write HTML file
    Path(html_file).write_text(html_complete, encoding='utf-8')
    print(f"[OK] Fichier HTML cree: {html_file}")
    print(f"\nInstructions:")
    print(f"  1. Le fichier HTML va s'ouvrir dans ton navigateur")
    print(f"  2. Appuie sur Ctrl+P (ou Cmd+P sur Mac)")
    print(f"  3. Choisis 'Enregistrer en PDF' comme destination")
    print(f"  4. Sauvegarde sous 'rapport_tp.pdf'")
    print(f"\nOuverture du navigateur...")

    # Open in browser
    html_path = os.path.abspath(html_file)
    webbrowser.open('file://' + html_path)

if __name__ == "__main__":
    convert_md_to_html("rapport_tp.md", "rapport_tp.html")
