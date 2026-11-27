# OralAI - PDF Screening Report Service

# Generates a professional PDF screening report containing:
# - Patient information
# - Screening information
# - AI prediction
# - Confidence
# - Risk status
# - Original oral image
# - Grad-CAM image
# - NLP AI explanation
# - Medical disclaimer


import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# BASE PATH

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "uploads",
    "reports"
)

os.makedirs(REPORT_DIR, exist_ok=True)

# HELPER - SAFE TEXT

def safe_text(value, default="Not available"):
    if value is None:
        return default

    value = str(value).strip()

    if value == "":
        return default

    return value

# HELPER - FORMAT DATE

def format_date(value):
    if value is None:
        return "Not available"

    try:
        return value.strftime("%d %B %Y")
    except Exception:
        return str(value)

# HELPER - FORMAT TIME

def format_time(value):
    if value is None:
        return "Not available"

    try:
        return value.strftime("%I:%M %p")
    except Exception:
        return str(value)

# HELPER - IMAGE PATH

def get_absolute_image_path(image_path):
    """
    Converts database image path into an absolute backend path.

    Example:
        uploads/user_7_106.jpeg

    becomes:

        D:/FYP/backend/uploads/user_7_106.jpeg
    """

    if not image_path:
        return None

    image_path = str(image_path).replace("\\", "/")

    # Remove leading slash if present
    image_path = image_path.lstrip("/")

    # If path already points to backend
    if os.path.isabs(image_path):
        return image_path

    return os.path.join(
        BASE_DIR,
        image_path
    )

# HELPER - ADD IMAGE

def add_report_image(story, image_path, width=150 * mm):
    """
    Adds an image to the PDF if it exists.
    """

    full_path = get_absolute_image_path(image_path)
    if not full_path:
        return

    if not os.path.exists(full_path):
        return

    try:
        img = Image(full_path)

        # Keep original aspect ratio
        original_width = img.imageWidth
        original_height = img.imageHeight

        if original_width == 0 or original_height == 0:
            return

        height = width * (
            original_height / original_width
        )

        # Prevent extremely tall images
        max_height = 90 * mm

        if height > max_height:
            height = max_height
            width = height * (
                original_width / original_height
            )

        img.drawWidth = width
        img.drawHeight = height

        story.append(
            img
        )

        story.append(
            Spacer(1, 5 * mm)
        )

    except Exception as e:
        print(
            f"PDF image error: {e}"
        )

# MAIN PDF GENERATOR

def generate_screening_report(
    patient,
    screening
):
    """
    Generate complete OralAI screening PDF.
    """

    screening_id = screening.get("id")

    filename = (
        f"OralAI_Screening_Report_{screening_id}.pdf"
    )

    output_path = os.path.join(
        REPORT_DIR,
        filename
    )

    # DOCUMENT

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    # CUSTOM STYLES

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=4 * mm
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=8 * mm
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=6 * mm,
        spaceAfter=4 * mm
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=15
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=colors.grey
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#555555")
    )

    # STORY
    story = []

    # HEADER
    story.append(
        Paragraph(
            "OralAI",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Oral Cancer Screening Support System",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            "SCREENING REPORT",
            section_style
        )
    )

    # PATIENT INFORMATION

    story.append(
        Paragraph(
            "Patient Information",
            section_style
        )
    )

    patient_name = safe_text(
        patient.get("fullname")
    )

    patient_email = safe_text(
        patient.get("email")
    )

    patient_data = [
        [
            Paragraph("<b>Patient Name</b>", normal_style),
            Paragraph(patient_name, normal_style)
        ],
        [
            Paragraph("<b>Email</b>", normal_style),
            Paragraph(patient_email, normal_style)
        ],
        [
            Paragraph("<b>Patient ID</b>", normal_style),
            Paragraph(
                safe_text(patient.get("id")),
                normal_style
            )
        ]
    ]

    patient_table = Table(
        patient_data,
        colWidths=[
            50 * mm,
            120 * mm
        ]
    )

    patient_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#f2f4f7")
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#d9d9d9")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(
        patient_table
    )

    # SCREENING INFORMATION
    # ========================================================

    story.append(
        Paragraph(
            "Screening Information",
            section_style
        )
    )

    created_at = screening.get(
        "created_at"
    )

    screening_data = [
        [
            Paragraph("<b>Screening ID</b>", normal_style),
            Paragraph(
                f"#{safe_text(screening.get('id'))}",
                normal_style
            )
        ],
        [
            Paragraph("<b>Date</b>", normal_style),
            Paragraph(
                format_date(created_at),
                normal_style
            )
        ],
        [
            Paragraph("<b>Time</b>", normal_style),
            Paragraph(
                format_time(created_at),
                normal_style
            )
        ],
        [
            Paragraph("<b>Age</b>", normal_style),
            Paragraph(
                safe_text(screening.get("age")),
                normal_style
            )
        ],
        [
            Paragraph("<b>Tobacco Usage</b>", normal_style),
            Paragraph(
                safe_text(screening.get("tobacco")),
                normal_style
            )
        ],
        [
            Paragraph("<b>Alcohol Usage</b>", normal_style),
            Paragraph(
                safe_text(screening.get("alcohol")),
                normal_style
            )
        ],
        [
            Paragraph("<b>Lesion Duration</b>", normal_style),
            Paragraph(
                safe_text(
                    screening.get("lesion_duration")
                ),
                normal_style
            )
        ],
        [
            Paragraph("<b>Previous Lesion History</b>", normal_style),
            Paragraph(
                safe_text(
                    screening.get("previous_lesion")
                ),
                normal_style
            )
        ]
    ]

    screening_table = Table(
        screening_data,
        colWidths=[
            65 * mm,
            105 * mm
        ]
    )

    screening_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#f2f4f7")
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#d9d9d9")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(
        screening_table
    )

    # ========================================================
    # AI SCREENING RESULT
    # ========================================================

    story.append(
        Paragraph(
            "AI Screening Result",
            section_style
        )
    )

    prediction = safe_text(
        screening.get("prediction")
    )

    confidence = screening.get(
        "confidence"
    )

    if confidence is not None:
        try:
            confidence_text = (
                f"{float(confidence):.2f}%"
            )
        except Exception:
            confidence_text = str(confidence)
    else:
        confidence_text = "Not available"

    risk_status = safe_text(
        screening.get("risk_status")
    )

    ai_data = [
        [
            Paragraph("<b>Prediction</b>", normal_style),
            Paragraph(
                prediction.upper(),
                normal_style
            )
        ],
        [
            Paragraph("<b>Model Confidence</b>", normal_style),
            Paragraph(
                confidence_text,
                normal_style
            )
        ],
        [
            Paragraph("<b>Risk Status</b>", normal_style),
            Paragraph(
                risk_status.upper(),
                normal_style
            )
        ]
    ]

    ai_table = Table(
        ai_data,
        colWidths=[
            65 * mm,
            105 * mm
        ]
    )

    ai_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#f2f4f7")
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#d9d9d9")
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(
        ai_table
    )

    # ========================================================
    # ORIGINAL IMAGE
    # ========================================================

    story.append(
        Paragraph(
            "Analysed Oral Image",
            section_style
        )
    )

    original_image = screening.get(
        "image_path"
    )

    add_report_image(
        story,
        original_image,
        width=145 * mm
    )

    # ========================================================
    # GRAD-CAM
    # ========================================================

    story.append(
        Paragraph(
            "Grad-CAM Explainability",
            section_style
        )
    )

    story.append(
        Paragraph(
            "The Grad-CAM visualization highlights image "
            "regions that contributed to the AI model's "
            "prediction.",
            normal_style
        )
    )

    story.append(
        Spacer(
            1,
            4 * mm
        )
    )

    gradcam_image = screening.get(
        "gradcam_path"
    )

    add_report_image(
        story,
        gradcam_image,
        width=145 * mm
    )

    # ========================================================
    # NLP EXPLANATION
    # ========================================================

    story.append(
        Paragraph(
            "AI Screening Explanation",
            section_style
        )
    )

    explanation = safe_text(
        screening.get("explanation"),
        "AI screening explanation is currently unavailable."
    )

    # Convert new lines into HTML breaks
    explanation = explanation.replace(
        "\n",
        "<br/>"
    )

    story.append(
        Paragraph(
            explanation,
            normal_style
        )
    )

    # ========================================================
    # DISCLAIMER
    # ========================================================

    story.append(
        Spacer(
            1,
            8 * mm
        )
    )

    disclaimer_data = [[
        Paragraph(
            "<b>Important Notice</b><br/><br/>"
            "This report contains an AI-generated screening "
            "result intended to support oral health screening "
            "and decision-making. It is not a final medical "
            "diagnosis. The prediction, confidence score, "
            "risk status and Grad-CAM visualization should "
            "be reviewed by a qualified clinician. Final "
            "diagnosis and clinical decisions must be made "
            "by an appropriately qualified healthcare "
            "professional.",
            disclaimer_style
        )
    ]]

    disclaimer_table = Table(
        disclaimer_data,
        colWidths=[
            170 * mm
        ]
    )

    disclaimer_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.HexColor("#f8f8f8")
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.7,
                colors.HexColor("#cccccc")
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10
            )
        ])
    )

    story.append(
        disclaimer_table
    )

    # ========================================================
    # FOOTER
    # ========================================================

    story.append(
        Spacer(
            1,
            8 * mm
        )
    )

    story.append(
        Paragraph(
            "Generated by OralAI",
            small_style
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(
        story
    )

    print(
        f"PDF report generated: {output_path}"
    )

    return output_path
