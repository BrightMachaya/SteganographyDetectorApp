"""Configuration and constants"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SteganographyDetector")

# Theme colors
BACKGROUND = "#F0F0F0"
SURFACE = "#FFFFFF"
PRIMARY = "#1976D2"
SECONDARY = "#388E3C"
ERROR = "#D32F2F"
SUCCESS = "#388E3C"
WARNING = "#F57C00"
TEXT_PRIMARY = "#000000"
TEXT_SECONDARY = "#666666"
BUTTON_NORMAL = "#FFFFFF"
BUTTON_HOVER = "#E0E0E0"
BUTTON_TEXT = "#000000"
BUTTON_HOVER_TEXT = "#000000"
INPUT_BG = "#FFFFFF"
INPUT_TEXT = "#000000"

# PDF availability
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False