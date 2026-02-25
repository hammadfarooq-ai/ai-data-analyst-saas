from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.config import settings


def generate_pdf_report(report_name: str, payload: dict) -> str:
    Path(settings.report_dir).mkdir(parents=True, exist_ok=True)
    report_path = Path(settings.report_dir) / report_name
    c = canvas.Canvas(str(report_path), pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "AI Data Analyst - Automated Report")
    y -= 30

    c.setFont("Helvetica", 10)
    sections = [
        ("Dataset Summary", payload.get("dataset_summary", {})),
        ("EDA Highlights", payload.get("eda_summary", {})),
        ("Model Comparison", payload.get("model_comparison", {})),
        ("Best Model Metrics", payload.get("best_metrics", {})),
        ("Feature Importance", payload.get("feature_importance", {})),
        ("Conclusion", payload.get("conclusion", "")),
    ]

    for title, content in sections:
        if y < 100:
            c.showPage()
            y = height - 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, title)
        y -= 18
        c.setFont("Helvetica", 9)
        text = str(content)
        for chunk in [text[i : i + 120] for i in range(0, len(text), 120)]:
            c.drawString(50, y, chunk)
            y -= 14
            if y < 80:
                c.showPage()
                y = height - 40

    c.save()
    return str(report_path)
