"""
PDF Generator Module
Generates PDF reports using ReportLab
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import io
from database import EconomicDatabase


def generate_pdf_report():
    """Generate PDF report with economic indicators"""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=1
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceBefore=20,
        spaceAfter=10
    )

    # Title
    title = Paragraph("Egypt Economic Indicators Report", title_style)
    story.append(title)

    # Subtitle with date
    date_text = Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", subtitle_style)
    story.append(date_text)
    story.append(Spacer(1, 0.5*inch))

    # Fetch data
    db = EconomicDatabase()
    gdp_df = db.get_all_gdp()
    inflation_df = db.get_all_inflation()
    exchange_df = db.get_all_exchange_rates()

    # Executive Summary
    summary_title = Paragraph("Executive Summary", section_style)
    story.append(summary_title)
    story.append(Spacer(1, 0.1*inch))

    if not gdp_df.empty:
        latest_gdp = gdp_df.iloc[-1]
        gdp_text = Paragraph(
            f"<b>Latest GDP:</b> ${latest_gdp['gdp_billions_usd']:.2f} billion USD ({int(latest_gdp['date'].year) if hasattr(latest_gdp['date'], 'year') else latest_gdp['date'][:4]})",
            styles['Normal']
        )
        story.append(gdp_text)
        story.append(Spacer(1, 0.1*inch))

    if not inflation_df.empty:
        latest_inflation = inflation_df.iloc[-1]
        inflation_text = Paragraph(
            f"<b>Latest Inflation Rate:</b> {latest_inflation['inflation_rate']:.2f}%",
            styles['Normal']
        )
        story.append(inflation_text)
        story.append(Spacer(1, 0.1*inch))

    if not exchange_df.empty:
        latest_exchange = exchange_df.iloc[-1]
        exchange_text = Paragraph(
            f"<b>Latest Exchange Rate:</b> {latest_exchange['usd_egp_rate']:.2f} EGP per USD",
            styles['Normal']
        )
        story.append(exchange_text)
        story.append(Spacer(1, 0.3*inch))

    # GDP Historical Table
    if not gdp_df.empty:
        gdp_title = Paragraph("GDP Historical Data (Last 5 Years)", section_style)
        story.append(gdp_title)
        story.append(Spacer(1, 0.1*inch))

        gdp_data = [['Year', 'GDP (Billions USD)']]
        for _, row in gdp_df.tail(5).iterrows():
            year = row['date'].year if hasattr(row['date'], 'year') else str(row['date'])[:4]
            gdp_data.append([str(year), f"${row['gdp_billions_usd']:.2f}"])

        gdp_table = Table(gdp_data, colWidths=[2*inch, 2*inch])
        gdp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(gdp_table)
        story.append(Spacer(1, 0.3*inch))

    # Inflation Historical Table
    if not inflation_df.empty:
        inflation_title = Paragraph("Inflation Rate Historical Data (Last 5 Years)", section_style)
        story.append(inflation_title)
        story.append(Spacer(1, 0.1*inch))

        inflation_data = [['Year', 'Inflation Rate (%)']]
        for _, row in inflation_df.tail(5).iterrows():
            year = row['date'].year if hasattr(row['date'], 'year') else str(row['date'])[:4]
            inflation_data.append([str(year), f"{row['inflation_rate']:.2f}%"])

        inflation_table = Table(inflation_data, colWidths=[2*inch, 2*inch])
        inflation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(inflation_table)
        story.append(Spacer(1, 0.3*inch))

    # Exchange Rate Historical Table
    if not exchange_df.empty:
        exchange_title = Paragraph("USD/EGP Exchange Rate (Recent)", section_style)
        story.append(exchange_title)
        story.append(Spacer(1, 0.1*inch))

        exchange_data = [['Date', 'Rate (EGP per USD)']]
        for _, row in exchange_df.tail(10).iterrows():
            date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])[:10]
            exchange_data.append([date_str, f"{row['usd_egp_rate']:.2f}"])

        exchange_table = Table(exchange_data, colWidths=[2*inch, 2*inch])
        exchange_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(exchange_table)

    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer = Paragraph(
        "Data sources: World Bank API, Exchange Rate API<br/>Report generated by Egypt Economic Dashboard",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#95a5a6'), alignment=1)
    )
    story.append(footer)

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


if __name__ == "__main__":
    # Test PDF generation
    pdf_buffer = generate_pdf_report()
    with open("test_report.pdf", "wb") as f:
        f.write(pdf_buffer.read())
    print("Test PDF generated: test_report.pdf")
