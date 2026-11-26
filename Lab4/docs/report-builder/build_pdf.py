#!/usr/bin/env python3
"""
Renders ../../REPORT.md to ../../Lab4_AdrianMutu_FAF-242.pdf with a UTM cover.

Documentation tooling only (Python + ReportLab); the application itself is C#.
REPORT.md stays the single source: headings, paragraphs, lists, tables and code
blocks are converted as they are, and each ```mermaid block marked with
<!-- figure: name --> is replaced by the matching vector diagram in figures.py.

    python3 docs/report-builder/build_pdf.py
"""

import os
import re
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table)
from reportlab.platypus.tableofcontents import TableOfContents

import styles
from styles import (BODY, BODY_B, GREY, MARGIN, PAGE_H, PAGE_W, RULE, S, USABLE, P,
                    data_table, listing)
import figures

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(os.path.dirname(HERE))
SOURCE = os.path.join(LAB, "REPORT.md")
OUTPUT = os.path.join(LAB, "Lab4_AdrianMutu_FAF-242.pdf")

COVER = {
    "discipline": "Software Design Techniques and Mechanisms (TMPS)",
    "lab_no": "4",
    "topic": "Behavioral Design Patterns in a Multi-Asset Portfolio Tracker",
    "student": "Adrian Mutu",
    "group": "FAF-242",
    "professor": "Daniel Istrati",
    "city_year": "Chișinău, 2026",
}

# Courier (base-14) has no box-drawing glyphs, which the project tree uses.
MONO_DIR = "/System/Library/Fonts/Supplemental/"
try:
    pdfmetrics.registerFont(TTFont("Mono", MONO_DIR + "Courier New.ttf"))
    MONO = "Mono"
except Exception:
    MONO = "Courier"
for name in ("code", "code_sm", "tbl_code"):
    S[name].fontName = MONO
S["code"].fontSize, S["code"].leading = 7.0, 8.8
S["h1"].keepWithNext = S["h2"].keepWithNext = 1
S["lead"] = ParagraphStyle("lead", parent=S["body"], alignment=TA_LEFT)
S["subhead"] = ParagraphStyle("subhead", parent=S["body"], alignment=TA_LEFT, keepWithNext=1,
                              spaceBefore=4, spaceAfter=4)
TABLE_CODE_SIZE = 7.0


# ---------------------------------------------------------------------------
# Markdown -> flowables
# ---------------------------------------------------------------------------

def inline(text, code_size=None):
    """Bold, inline code and links; everything else is escaped."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    size = " size='%s'" % code_size if code_size else ""
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append("<font name='%s'%s>%s</font>" % (MONO, size, escape(part[1:-1])))
            continue
        part = escape(part)
        part = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", part)
        part = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", part)
        out.append(part)
    text = "".join(out)
    # [label](target) -> label (relative repository links mean nothing on paper)
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)


def table(lines):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
    ncol = len(rows[0])

    def word_width(word):
        if word.startswith("`"):
            return pdfmetrics.stringWidth(word.strip("`(),.:"), MONO, TABLE_CODE_SIZE)
        return pdfmetrics.stringWidth(word.strip("*"), BODY_B, 9.2)

    minimum = [max(word_width(w) for r in rows for w in re.findall(r"`[^`]+`|\S+", r[i])) + 14
               for i in range(ncol)]
    # Spare width goes to columns with text that can actually wrap; a column of
    # single long identifiers (test names) needs only its minimum.
    def wrappable(cell):
        plain = re.sub(r"[`*]", "", cell)
        return len(plain) - max((len(w) for w in plain.split()), default=0)

    weights = [max(wrappable(r[i]) for r in rows) + 1 for i in range(ncol)]
    spare = USABLE - sum(minimum)
    if spare > 0:
        widths = [m + spare * w / sum(weights) for m, w in zip(minimum, weights)]
    else:
        widths = [USABLE * m / sum(minimum) for m in minimum]
    cells = [[inline(c, code_size=TABLE_CODE_SIZE) for c in r] for r in rows]
    return [data_table(cells, widths), Spacer(1, 8)]


def convert(markdown):
    lines = markdown.splitlines()
    # The title block before the first section is replaced by the cover page.
    start = next(i for i, l in enumerate(lines) if l.startswith("## "))
    lines = lines[start:]
    story, para, i, figure = [], [], 0, None

    def flush():
        if para:
            text = " ".join(para)
            if re.fullmatch(r"\*\*[^*]+\*\*", text):   # a bold-only line is a sub-heading
                style = "subhead"
            else:
                style = "lead" if text.endswith(":") else "body"
            story.append(P(inline(text), style))
            para.clear()

    def add_block(flowables):
        """
        A block keeps its short lead-in paragraph, and any headings right above
        it, on the same page. (ReportLab's keepWithNext does not merge a heading
        into a KeepTogether, so the grouping is done here.)
        """
        lead = []
        if story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("lead", "body") \
                and len(story[-1].getPlainText()) < 220:
            lead.insert(0, story.pop())
        while story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("h1", "h2"):
            lead.insert(0, story.pop())
        story.append(KeepTogether(lead + flowables))

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        marker = re.match(r"<!--\s*figure:\s*(\w+)\s*-->", stripped)
        if marker:
            flush(); figure = marker.group(1); i += 1; continue
        if stripped.startswith("```"):
            flush()
            lang = stripped[3:].strip()
            body = []
            i += 1
            while not lines[i].strip().startswith("```"):
                body.append(lines[i]); i += 1
            i += 1
            if lang == "mermaid":
                drawing = figures.FIGURES[figure]()
                caption = ""
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines) and re.fullmatch(r"\*Figure .+\*", lines[i].strip()):
                    caption = lines[i].strip()[1:-1]; i += 1
                add_block([drawing, P(inline(caption), "caption")])
                figure = None
            else:
                code = "\n".join(body)
                widest = max(len(l) for l in body) if body else 1
                size = min(7.0, (USABLE - 16) / (0.6 * widest))  # shrink long logs to fit
                style = ParagraphStyle("code_fit", parent=S["code"], fontSize=size,
                                       leading=size * 1.27)
                S["code_fit"] = style
                add_block([listing(code, fs="code_fit"), Spacer(1, 8)])
            continue
        if stripped.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i]); i += 1
            add_block(table(block))
            continue
        if stripped.startswith("## "):
            flush(); story.append(P(inline(stripped[3:]), "h1")); i += 1; continue
        if stripped.startswith("### "):
            flush(); story.append(P(inline(stripped[4:]), "h2")); i += 1; continue
        if stripped.startswith("- "):
            flush()
            item = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                item.append(lines[i].strip()); i += 1
            story.append(Paragraph(inline(" ".join(item)), S["bullet"], bulletText="•"))
            continue
        if not stripped:
            flush(); i += 1; continue
        para.append(stripped)
        i += 1
    flush()
    return story


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class ReportDoc(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ("h1", "h2"):
            level = 0 if flowable.style.name == "h1" else 1
            self.notify("TOCEntry", (level, flowable.getPlainText(), self.page))


def body_page(canvas, doc):
    canvas.saveState()
    canvas.setFont(BODY, 8)
    canvas.setFillColor(GREY)
    canvas.drawString(MARGIN, PAGE_H - MARGIN + 14, "UTM – FCIM – %s" % COVER["discipline"])
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN + 14,
                           "Laboratory Work No. %s" % COVER["lab_no"])
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN, PAGE_H - MARGIN + 9, PAGE_W - MARGIN, PAGE_H - MARGIN + 9)
    canvas.line(MARGIN, MARGIN - 16, PAGE_W - MARGIN, MARGIN - 16)
    canvas.setFont(BODY, 9)
    canvas.drawCentredString(PAGE_W / 2.0, MARGIN - 28, str(canvas.getPageNumber()))
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.8)
    canvas.rect(MARGIN - 14, MARGIN - 14, PAGE_W - 2 * MARGIN + 28, PAGE_H - 2 * MARGIN + 28)
    canvas.restoreState()


def cover():
    logo = Image(os.path.join(HERE, "utm_logo.jpg"), width=4.92 * cm, height=2.54 * cm)
    logo.hAlign = "CENTER"
    checked = Table([[Paragraph("Checked by:<br/>%s<br/>FCIM, UTM" % COVER["professor"],
                                S["cover_right"])]], colWidths=[6.5 * cm])
    checked.hAlign = "RIGHT"
    return [
        Spacer(1, 6), logo, Spacer(1, 14),
        P("MINISTRY OF EDUCATION AND RESEARCH OF THE REPUBLIC OF MOLDOVA", "cover_caps"),
        P("Technical University of Moldova", "cover_small"),
        P("Faculty of Computers, Informatics and Microelectronics", "cover_small"),
        P("Department of Software Engineering and Automation", "cover_small"),
        Spacer(1, 1.9 * cm),
        P(COVER["student"], "cover_small"),
        P("Group: %s" % COVER["group"], "cover_small"),
        Spacer(1, 2.4 * cm),
        P("Report", "cover_title"),
        P("Laboratory Work No. %s" % COVER["lab_no"], "cover_topic"),
        P(COVER["discipline"], "cover_topic"),
        Spacer(1, 0.5 * cm),
        P("<b>Topic:</b> %s" % COVER["topic"], "cover_topic"),
        Spacer(1, 2.3 * cm),
        checked, Spacer(1, 1.6 * cm),
        P(COVER["city_year"], "cover_small"),
    ]


def build():
    with open(SOURCE, encoding="utf-8") as handle:
        content = convert(handle.read())
    doc = ReportDoc(OUTPUT, pagesize=(PAGE_W, PAGE_H), leftMargin=MARGIN, rightMargin=MARGIN,
                    topMargin=MARGIN, bottomMargin=MARGIN, author=COVER["student"],
                    title="Laboratory Work No. %s – %s" % (COVER["lab_no"], COVER["topic"]))
    frame = Frame(MARGIN, MARGIN, USABLE, PAGE_H - 2 * MARGIN, id="body")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=cover_page),
                          PageTemplate(id="body", frames=[frame], onPage=body_page)])
    toc = TableOfContents()
    toc.levelStyles = [S["toc1"], S["toc2"]]
    story = cover() + [NextPageTemplate("body"), PageBreak(),
                       P("Contents", "h1_notoc"), toc, PageBreak()] + content
    doc.multiBuild(story)
    print("wrote %s" % OUTPUT)


if __name__ == "__main__":
    build()
