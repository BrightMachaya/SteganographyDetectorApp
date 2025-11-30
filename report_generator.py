"""PDF and report generation functionality"""
import os
from datetime import datetime
from typing import Dict
from config import logger, PDF_AVAILABLE

if PDF_AVAILABLE:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

class PDFReportGenerator:
    """Generate PDF reports for steganography analysis"""
    
    @staticmethod
    def generate_pdf_report(results: Dict, output_dir: str, source_folder: str) -> str:
        """Generate a comprehensive PDF report"""
        if not PDF_AVAILABLE:
            return "PDF generation not available"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = os.path.join(output_dir, f"steganography_report_{timestamp}.pdf")
            
            doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.5*inch)
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.black,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.black,
                spaceAfter=12,
                spaceBefore=12
            )
            
            danger_style = ParagraphStyle(
                'DangerText',
                parent=styles['Normal'],
                textColor=colors.red,
                fontSize=10,
                spaceAfter=6
            )
            
            success_style = ParagraphStyle(
                'SuccessText',
                parent=styles['Normal'],
                textColor=colors.green,
                fontSize=10,
                spaceAfter=6
            )
            
            warning_style = ParagraphStyle(
                'WarningText',
                parent=styles['Normal'],
                textColor=colors.orange,
                fontSize=10,
                spaceAfter=6
            )
            
            story = []
            
            story.append(Paragraph("Steganography Detection Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph("Executive Summary", heading_style))
            
            summary_data = [
                ["Analysis Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["Source Folder:", source_folder],
                ["Output Folder:", output_dir],
                ["Total Files Processed:", str(len(results['clean_files']) + len(results['suspicious_files']) + len(results['confirmed_steg_files']))],
                ["Clean Files:", str(len(results['clean_files']))],
                ["Suspicious Files:", str(len(results['suspicious_files']))],
                ["Confirmed Steganography:", str(len(results['confirmed_steg_files']))],
                ["Files Extracted:", str(len(results['all_extracted_files']))],
                ["Analysis Errors:", str(len(results['errors']))]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2D2D2D")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F8F8")),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            if results['confirmed_steg_files']:
                story.append(Paragraph("🚨 Confirmed Steganography Cases", heading_style))
                
                confirmed_data = [["File", "Payload Size", "Content Type", "Method"]]
                for result in results['confirmed_steg_files']:
                    file_path = result['file_analyzed']
                    payload_info = result['analyzer_results']['extraction_results']
                    confirmed_data.append([
                        os.path.basename(file_path),
                        f"{payload_info.get('payload_size', 0):,} bytes",
                        payload_info.get('content_type', 'Unknown'),
                        payload_info.get('method', 'Unknown')
                    ])
                
                confirmed_table = Table(confirmed_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
                confirmed_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#FFE6E6")),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(confirmed_table)
                story.append(Spacer(1, 0.2*inch))
            
            if results['all_extracted_files']:
                story.append(Paragraph("📁 Extracted Files", heading_style))
                
                extracted_data = [["Filename", "Type", "Size", "Location"]]
                for file_info in results['all_extracted_files']:
                    extracted_data.append([
                        file_info['filename'],
                        file_info['type'],
                        f"{file_info['size']:,} bytes",
                        "Output Folder"
                    ])
                
                extracted_table = Table(extracted_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.5*inch])
                extracted_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2D2D2D")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F8F8")),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(extracted_table)
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("🔍 Risk Assessment", heading_style))
            
            if results['confirmed_steg_files']:
                story.append(Paragraph(
                    f"HIGH RISK: {len(results['confirmed_steg_files'])} files confirmed to contain hidden data",
                    danger_style
                ))
                story.append(Paragraph(
                    "Immediate action required. Investigate source and intent of hidden data.",
                    styles['Normal']
                ))
            
            if results['suspicious_files']:
                story.append(Paragraph(
                    f"MEDIUM RISK: {len(results['suspicious_files'])} files show suspicious characteristics",
                    warning_style
                ))
                story.append(Paragraph(
                    "Further investigation recommended. Monitor these files and their sources.",
                    styles['Normal']
                ))
            
            if not results['confirmed_steg_files'] and not results['suspicious_files']:
                story.append(Paragraph(
                    f"LOW RISK: No steganography detected",
                    success_style
                ))
                story.append(Paragraph(
                    "No immediate action required. Maintain standard security monitoring.",
                    styles['Normal']
                ))
            
            doc.build(story)
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return f"PDF generation failed: {str(e)}"