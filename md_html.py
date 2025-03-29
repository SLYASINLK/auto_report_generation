import markdown
import tempfile
import webbrowser
from pathlib import Path
def render_markdown_to_browser(markdown_text, output_file="temp_report.html", keep_file=False):
    """
    Render Markdown string to HTML and open in browser
    
    Parameters:
        markdown_text (str): Markdown text to render
        output_file (str): Output HTML filename, defaults to 'temp_report.html'
        keep_file (bool): Whether to keep the HTML file, defaults to False (temporary file)
    """

    html_content = markdown.markdown(markdown_text, extensions=['tables', 'extra'])
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            max-width: 1000px;
            margin-left: auto;
            margin-right: auto;
            color: #333;
            background-color: #f9f9f9;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        h2 {{
            color: #2980b9;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        h3 {{
            color: #3498db;
            font-weight: normal;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        ul, ol {{
            margin-left: 20px;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        strong {{
            color: #2c3e50;
        }}
        code {{
            background-color: #f0f0f0;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: Consolas, monospace;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            color: #555;
            margin-left: 0;
        }}
        .conclusion {{
            background-color: #e8f4fc;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 25px 0;
            border-radius: 0 4px 4px 0;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    # Process output file
    if keep_file:
        # Save to specified file
        output_path = Path(output_file)
        output_path.write_text(full_html, encoding='utf-8')
    else:
        # Create temporary file
        output_path = Path(tempfile.mktemp(suffix='.html'))
        output_path.write_text(full_html, encoding='utf-8')
    
    # Open in browser
    webbrowser.open(f'file://{output_path.resolve()}')
    
    if keep_file:
        print(f"Report saved and opened: {output_path.resolve()}")
    else:
        print(f"Temporary report opened: {output_path.resolve()} (will be deleted after closing browser)")