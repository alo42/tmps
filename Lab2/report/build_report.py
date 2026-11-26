#!/usr/bin/env python3
"""
Builds the Lab 2 report PDF.

    python3 report/build_report.py

Runs the program and the tests to capture their real output, renders the UML
figures from the live code, and writes ../Lab2_AdrianMutu_FAF-242.pdf.
"""

import os

from reportlab.lib.units import cm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table)
from reportlab.platypus.tableofcontents import TableOfContents

from styles import (BODY, GREY, MARGIN, PAGE_H, PAGE_W, RULE, S, USABLE, P)
import content

COVER = {
    "university": "Technical University of Moldova",
    "faculty": "Faculty of Computers, Informatics and Microelectronics",
    "department": "Department of Software Engineering and Automation",
    "discipline": "Software Design Techniques and Mechanisms (TMPS)",
    "lab_no": "2",
    "topic": "Creational and Structural Design Patterns in a Multi-Asset Portfolio Tracker",
    "student": "Adrian Mutu",
    "group": "FAF-242",
    "professor": "Daniel Istrati",
    "city_year": "Chișinău, 2026",
}

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "utm_logo.jpg")
OUTPUT = os.path.join(os.path.dirname(HERE), "Lab%s_AdrianMutu_FAF-242.pdf" % COVER["lab_no"])


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


def cover_story():
    out = []
    if os.path.exists(LOGO):
        img = Image(LOGO, width=4.92 * cm, height=2.54 * cm)
        img.hAlign = "CENTER"
        out += [Spacer(1, 6), img, Spacer(1, 14)]
    out += [
        P("MINISTRY OF EDUCATION AND RESEARCH OF THE REPUBLIC OF MOLDOVA", "cover_caps"),
        P(COVER["university"], "cover_small"),
        P(COVER["faculty"], "cover_small"),
        P(COVER["department"], "cover_small"),
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
    ]
    checked = Table([[Paragraph("Checked by:<br/>%s<br/>FCIM, UTM" % COVER["professor"],
                                S["cover_right"])]], colWidths=[6.5 * cm])
    checked.hAlign = "RIGHT"
    out += [checked, Spacer(1, 1.6 * cm), P(COVER["city_year"], "cover_small")]
    return out


def build():
    doc = ReportDoc(OUTPUT, pagesize=(PAGE_W, PAGE_H), leftMargin=MARGIN,
                    rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
                    title="Laboratory Work No. %s – %s" % (COVER["lab_no"], COVER["topic"]),
                    author=COVER["student"])
    frame = Frame(MARGIN, MARGIN, USABLE, PAGE_H - 2 * MARGIN, id="body")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame], onPage=cover_page),
        PageTemplate(id="body", frames=[frame], onPage=body_page),
    ])
    toc = TableOfContents()
    toc.levelStyles = [S["toc1"], S["toc2"]]
    story = cover_story() + [NextPageTemplate("body"), PageBreak(),
                             P("Contents", "h1_notoc"), toc, PageBreak()]
    story += content.story()
    doc.multiBuild(story)
    print("wrote %s" % OUTPUT)


if __name__ == "__main__":
    build()
