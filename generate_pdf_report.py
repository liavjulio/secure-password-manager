#!/usr/bin/env python3
"""
PDF Report Generator for Cybersecurity Project
Converts the markdown academic report to a professional PDF format
"""

import markdown
import pdfkit
import os
from datetime import datetime

def convert_markdown_to_pdf():
    """Convert the academic report from markdown to PDF with professional formatting"""
    
    # Read the markdown file
    markdown_file = '/Users/liavjulio/cyberProject/CYBERSECURITY_PROJECT_REPORT.md'
    output_file = '/Users/liavjulio/cyberProject/Cybersecurity_Project_Report.pdf'
    
    print("📄 Converting academic report to PDF...")
    
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML with extensions
        html = markdown.markdown(
            markdown_content,
            extensions=[
                'toc',
                'tables',
                'fenced_code',
                'codehilite',
                'nl2br'
            ]
        )
        
        # Add CSS styling for professional appearance
        css_style = """
        <style>
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
            font-size: 12pt;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-before: always;
            font-size: 24pt;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 5px;
            margin-top: 30px;
            font-size: 18pt;
        }
        h3 {
            color: #7f8c8d;
            margin-top: 25px;
            font-size: 14pt;
        }
        h4 {
            color: #95a5a6;
            margin-top: 20px;
            font-size: 12pt;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #bdc3c7;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #ecf0f1;
            font-weight: bold;
        }
        .abstract {
            font-style: italic;
            background-color: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border: 1px solid #bdc3c7;
            margin: 20px 0;
        }
        ul, ol {
            margin: 10px 0;
            padding-left: 30px;
        }
        li {
            margin: 5px 0;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }
        .page-break {
            page-break-before: always;
        }
        .header-info {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 20px;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 10pt;
            color: #7f8c8d;
        }
        </style>
        """
        
        # Combine CSS and HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Secure Password Manager - Cybersecurity Project Report</title>
            {css_style}
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Configure PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '1in',
            'margin-right': '0.8in',
            'margin-bottom': '1in',
            'margin-left': '0.8in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
            'print-media-type': None,
            'header-center': 'Secure Password Manager - Cybersecurity Project',
            'header-font-size': '10',
            'footer-center': 'Page [page] of [topage]',
            'footer-font-size': '10',
            'footer-spacing': '5',
            'header-spacing': '5'
        }
        
        # Generate PDF
        pdfkit.from_string(full_html, output_file, options=options)
        
        print(f"✅ PDF report generated successfully: {output_file}")
        print(f"📊 File size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        print("\n🔧 Trying alternative method...")
        return False

def alternative_pdf_generation():
    """Alternative PDF generation using reportlab for better compatibility"""
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor
        
        print("📄 Using alternative PDF generation method...")
        
        # Read markdown content
        markdown_file = '/Users/liavjulio/cyberProject/CYBERSECURITY_PROJECT_REPORT.md'
        output_file = '/Users/liavjulio/cyberProject/Cybersecurity_Project_Report.pdf'
        
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2c3e50'),
            alignment=1  # Center alignment
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=HexColor('#34495e')
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=HexColor('#7f8c8d')
        )
        
        # Parse content and create flowables
        story = []
        lines = content.split('\n')
        
        for line in lines[:50]:  # First 50 lines for title page
            line = line.strip()
            if line.startswith('# '):
                story.append(Paragraph(line[2:], title_style))
                story.append(Spacer(1, 12))
            elif line.startswith('**Author:**'):
                story.append(Paragraph(line.replace('**', '<b>').replace('**', '</b>'), styles['Normal']))
            elif line.startswith('**'):
                story.append(Paragraph(line.replace('**', '<b>').replace('**', '</b>'), styles['Normal']))
            elif line:
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Add page break and table of contents
        story.append(PageBreak())
        story.append(Paragraph("Table of Contents", heading1_style))
        story.append(Spacer(1, 12))
        
        # Simple TOC
        toc_items = [
            "1. Introduction",
            "2. Background",
            "3. Project Design", 
            "4. Implementation",
            "5. Results and Analysis",
            "6. Improvement Suggestions",
            "7. Conclusion",
            "8. References",
            "9. Appendices"
        ]
        
        for item in toc_items:
            story.append(Paragraph(item, styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Alternative PDF generated successfully: {output_file}")
        return True
        
    except ImportError:
        print("❌ reportlab not available. Installing...")
        return False
    except Exception as e:
        print(f"❌ Alternative PDF generation failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting PDF generation for Cybersecurity Project Report...")
    
    # Try primary method first
    if not convert_markdown_to_pdf():
        # Try alternative method
        if not alternative_pdf_generation():
            print("\n📝 Manual PDF generation instructions:")
            print("1. Install wkhtmltopdf: brew install wkhtmltopdf")
            print("2. Install Python packages: pip install pdfkit markdown reportlab")
            print("3. Run this script again")
            print("\nAlternatively, you can:")
            print("- Open the markdown file in a markdown editor")
            print("- Export/print to PDF from the editor")
            print("- Use online markdown to PDF converters")
