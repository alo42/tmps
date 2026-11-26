"""Page geometry, fonts, palette, paragraph styles and flowable helpers."""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Preformatted, Table, TableStyle

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
USABLE = PAGE_W - 2 * MARGIN

# ---------------------------------------------------------------------------
# Fonts - Arial carries Romanian diacritics; Helvetica (base-14) does not.
# ---------------------------------------------------------------------------

BODY, BODY_B, BODY_I = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
MONO = "Courier"


def register_fonts():
    global BODY, BODY_B, BODY_I
    base = "/System/Library/Fonts/Supplemental/"
    faces = {
        "Body": "Arial.ttf",
        "Body-Bold": "Arial Bold.ttf",
        "Body-Italic": "Arial Italic.ttf",
    }
    try:
        for name, filename in faces.items():
            pdfmetrics.registerFont(TTFont(name, os.path.join(base, filename)))
        pdfmetrics.registerFontFamily(
            "Body", normal="Body", bold="Body-Bold", italic="Body-Italic",
            boldItalic="Body-Bold")
        BODY, BODY_B, BODY_I = "Body", "Body-Bold", "Body-Italic"
    except Exception:
        pass  # fall back to the base-14 fonts declared above


register_fonts()

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

NAVY = colors.HexColor("#1F3864")
INK = colors.HexColor("#1A1A1A")
GREY = colors.HexColor("#6B6B6B")
RULE = colors.HexColor("#B8C4DA")
CODE_BG = colors.HexColor("#F6F7F9")
ABSTRACT_FILL = colors.HexColor("#E7EEF9")
IFACE_FILL = colors.HexColor("#FFF3E0")
CONCRETE_FILL = colors.white
NEW_FILL = colors.HexColor("#E6F4EA")
PKG_FILL = colors.HexColor("#F2F2F5")

# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------

S = {}
S["body"] = ParagraphStyle("body", fontName=BODY, fontSize=10.5, leading=15.2,
                           alignment=TA_JUSTIFY, textColor=INK, spaceAfter=7)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], leftIndent=16,
                             bulletIndent=4, spaceAfter=3.5)
S["h1"] = ParagraphStyle("h1", fontName=BODY_B, fontSize=14.5, leading=19,
                         textColor=NAVY, spaceBefore=16, spaceAfter=9)
S["h1_notoc"] = ParagraphStyle("h1_notoc", fontName=BODY_B, fontSize=14.5,
                               leading=19, textColor=NAVY, spaceBefore=16,
                               spaceAfter=9)
S["h2"] = ParagraphStyle("h2", fontName=BODY_B, fontSize=11.8, leading=16,
                         textColor=NAVY, spaceBefore=12, spaceAfter=6)
S["caption"] = ParagraphStyle("caption", fontName=BODY_I, fontSize=9, leading=12.5,
                              alignment=TA_CENTER, textColor=GREY,
                              spaceBefore=5, spaceAfter=12)
S["code"] = ParagraphStyle("code", fontName=MONO, fontSize=7.4, leading=9.4,
                           textColor=INK)
S["code_sm"] = ParagraphStyle("code_sm", fontName=MONO, fontSize=6.3, leading=7.9,
                              textColor=INK)
S["cover_small"] = ParagraphStyle("cover_small", fontName=BODY, fontSize=11.5,
                                  leading=16, alignment=TA_CENTER, textColor=INK)
S["cover_caps"] = ParagraphStyle("cover_caps", fontName=BODY_B, fontSize=11,
                                 leading=16, alignment=TA_CENTER, textColor=INK)
S["cover_title"] = ParagraphStyle("cover_title", fontName=BODY_B, fontSize=20,
                                  leading=26, alignment=TA_CENTER, textColor=NAVY)
S["cover_topic"] = ParagraphStyle("cover_topic", fontName=BODY, fontSize=13,
                                  leading=18, alignment=TA_CENTER, textColor=INK)
S["cover_right"] = ParagraphStyle("cover_right", fontName=BODY, fontSize=11.5,
                                  leading=17, alignment=TA_LEFT, textColor=INK)
S["toc1"] = ParagraphStyle("toc1", fontName=BODY_B, fontSize=10.8, leading=17,
                           textColor=INK)
S["toc2"] = ParagraphStyle("toc2", fontName=BODY, fontSize=10.2, leading=15,
                           leftIndent=16, textColor=INK)
S["tbl"] = ParagraphStyle("tbl", fontName=BODY, fontSize=9.2, leading=12.6,
                          textColor=INK)
S["tbl_b"] = ParagraphStyle("tbl_b", fontName=BODY_B, fontSize=9.2, leading=12.6,
                            textColor=colors.white)
S["tbl_code"] = ParagraphStyle("tbl_code", fontName=MONO, fontSize=8.3,
                               leading=11.6, textColor=INK)


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items, bullet="•"):
    return [Paragraph(t, S["bullet"], bulletText=bullet) for t in items]


def listing(code, fs="code"):
    """A code listing inside a light, bordered box."""
    tbl = Table([[Preformatted(code.strip("\n"), S[fs])]], colWidths=[USABLE])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def data_table(rows, widths, header=True):
    body = []
    for i, row in enumerate(rows):
        style = "tbl_b" if (header and i == 0) else "tbl"
        body.append([Paragraph(str(c), S[style]) for c in row])
    tbl = Table(body, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), NAVY),
                 ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F8FA")])]
    tbl.setStyle(TableStyle(cmds))
    return tbl


S["file"] = ParagraphStyle("file", fontName=MONO, fontSize=8.6, leading=12,
                           textColor=NAVY, spaceBefore=8, spaceAfter=4)
S["h1_notoc"] = ParagraphStyle("h1_notoc", parent=S["h1"])
S["ref"] = ParagraphStyle("ref", parent=S["bullet"], alignment=TA_LEFT)
