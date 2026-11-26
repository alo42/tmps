#!/usr/bin/env python3
"""
Builds `report.pdf` - the laboratory-work report for wealth_dashboard.py.

Everything (text, UML diagrams, code listings) is generated offline with
ReportLab. Edit the COVER dictionary below, drop the UTM logo next to this
script, then run:  python3 make_report.py
"""

import glob
import os
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import (Drawing, Group, Line, Polygon, PolyLine,
                                       Rect, String)
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

# ---------------------------------------------------------------------------
# COVER PAGE DATA - edit these five lines and re-run.
# ---------------------------------------------------------------------------

COVER = {
    "university": "Technical University of Moldova",
    "faculty": "Faculty of Computers, Informatics and Microelectronics",
    "department": "Department of Software Engineering and Automation",
    "discipline": "Software Design Techniques and Mechanisms (TMPS)",
    "lab_no": "1",
    "topic": "SOLID Principles in the Design of a Multi-Asset Portfolio Tracker",
    "student": "Adrian Mutu",
    "group": "FAF-242",
    "professor": "Daniel Istrati",
    "city_year": "Chișinău, 2026",
}

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(HERE, "wealth_dashboard.py")
OUTPUT_FILE = os.path.join(HERE, "report.pdf")

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
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), NAVY),
                 ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F8FA")])]
    tbl.setStyle(TableStyle(cmds))
    return tbl


# ---------------------------------------------------------------------------
# UML primitives
# ---------------------------------------------------------------------------

NAME_FS = 8.2
MEM_FS = 6.9
LH = 8.8
PAD = 4.0


class Box(object):
    """A UML classifier box with optional stereotype / attribute / method rows."""

    def __init__(self, x, y, w, name, stereo=None, attrs=(), methods=(),
                 fill=CONCRETE_FILL, abstract=False, tag=None):
        self.x, self.y, self.w = float(x), float(y), float(w)  # y = TOP edge
        self.name = name
        self.stereo = stereo
        self.attrs = list(attrs)
        self.methods = list(methods)
        self.fill = fill
        self.abstract = abstract
        self.tag = tag  # small note printed under the box

    @property
    def head_h(self):
        return 2 * PAD + (LH if self.stereo else 0) + NAME_FS + 2

    @property
    def h(self):
        total = self.head_h
        for comp in (self.attrs, self.methods):
            if comp:
                total += 2 * PAD + LH * len(comp) - (LH - MEM_FS - 2)
        return total

    @property
    def bottom(self):
        return self.y - self.h

    @property
    def right(self):
        return self.x + self.w

    @property
    def cx(self):
        return self.x + self.w / 2.0

    @property
    def cy(self):
        return self.y - self.h / 2.0

    def anchor(self, side, offset=0.0):
        if side == "top":
            return (self.cx + offset, self.y)
        if side == "bottom":
            return (self.cx + offset, self.bottom)
        if side == "left":
            return (self.x, self.cy + offset)
        if side == "right":
            return (self.right, self.cy + offset)
        raise ValueError(side)

    def draw(self, d):
        d.add(Rect(self.x, self.bottom, self.w, self.h, fillColor=self.fill,
                   strokeColor=NAVY, strokeWidth=0.8))
        cursor = self.y - PAD
        if self.stereo:
            cursor -= MEM_FS + 1
            d.add(String(self.cx, cursor, "«%s»" % self.stereo,
                         fontName=BODY_I, fontSize=MEM_FS, fillColor=GREY,
                         textAnchor="middle"))
            cursor -= 2
        cursor -= NAME_FS
        d.add(String(self.cx, cursor, self.name,
                     fontName=BODY_I if self.abstract else BODY_B,
                     fontSize=NAME_FS, fillColor=NAVY, textAnchor="middle"))
        edge = self.y - self.head_h
        for comp in (self.attrs, self.methods):
            if not comp:
                continue
            d.add(Line(self.x, edge, self.right, edge, strokeColor=NAVY,
                       strokeWidth=0.6))
            row = edge - PAD
            for item in comp:
                row -= MEM_FS + 1.6
                italic = item.endswith("*")
                d.add(String(self.x + 5, row, item.rstrip("*"),
                             fontName=BODY_I if italic else BODY,
                             fontSize=MEM_FS, fillColor=INK))
            edge = row - PAD + 1
        if self.tag:
            d.add(String(self.cx, self.bottom - 10, self.tag, fontName=BODY_I,
                         fontSize=6.6, fillColor=colors.HexColor("#1E7B34"),
                         textAnchor="middle"))


def _unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = (dx * dx + dy * dy) ** 0.5 or 1.0
    return dx / length, dy / length


def _triangle(d, p, q, size=7.5, fill=colors.white):
    """Hollow triangle head at q (inheritance / realization)."""
    ux, uy = _unit(p, q)
    bx, by = q[0] - ux * size, q[1] - uy * size
    px, py = -uy * size * 0.55, ux * size * 0.55
    d.add(Polygon([q[0], q[1], bx + px, by + py, bx - px, by - py],
                  fillColor=fill, strokeColor=NAVY, strokeWidth=0.8))


def _open_arrow(d, p, q, size=6.0):
    ux, uy = _unit(p, q)
    bx, by = q[0] - ux * size, q[1] - uy * size
    px, py = -uy * size * 0.45, ux * size * 0.45
    d.add(PolyLine([bx + px, by + py, q[0], q[1], bx - px, by - py],
                   strokeColor=NAVY, strokeWidth=0.8))


def _diamond(d, p, q, size=7.0, fill=colors.white):
    """Diamond at p, pointing along p->q (aggregation / composition)."""
    ux, uy = _unit(p, q)
    tipx, tipy = p[0], p[1]
    farx, fary = p[0] + ux * size * 1.8, p[1] + uy * size * 1.8
    midx, midy = p[0] + ux * size * 0.9, p[1] + uy * size * 0.9
    px, py = -uy * size * 0.5, ux * size * 0.5
    d.add(Polygon([tipx, tipy, midx + px, midy + py, farx, fary, midx - px, midy - py],
                  fillColor=fill, strokeColor=NAVY, strokeWidth=0.8))


def connect(d, pts, kind="assoc", label=None, label_at=None, label_dx=0, label_dy=0):
    """
    Draw a connector through `pts` (list of (x, y) waypoints).
    kind: inherit | realize | dep | assoc | compose | plain
    """
    flat = [c for pt in pts for c in pt]
    dash = (2.2, 2.2) if kind in ("realize", "dep") else None
    d.add(PolyLine(flat, strokeColor=NAVY, strokeWidth=0.8, strokeDashArray=dash))
    tail, head = pts[-2], pts[-1]
    if kind in ("inherit", "realize"):
        _triangle(d, tail, head)
    elif kind in ("dep", "assoc"):
        _open_arrow(d, tail, head)
    elif kind == "compose":
        _diamond(d, pts[0], pts[1], fill=NAVY)
        _open_arrow(d, tail, head)
    if label:
        lx, ly = label_at if label_at else ((pts[0][0] + pts[-1][0]) / 2.0,
                                           (pts[0][1] + pts[-1][1]) / 2.0)
        d.add(String(lx + label_dx, ly + label_dy, label, fontName=BODY_I,
                     fontSize=6.6, fillColor=GREY, textAnchor="middle"))


def package(d, x, y, w, h, title, fill=PKG_FILL):
    """UML package shape: a tab plus a body rectangle."""
    tab_w, tab_h = min(w * 0.46, 118), 12
    d.add(Rect(x, y - tab_h, tab_w, tab_h, fillColor=fill, strokeColor=NAVY,
               strokeWidth=0.8))
    d.add(Rect(x, y - h, w, h - tab_h, fillColor=fill, strokeColor=NAVY,
               strokeWidth=0.8))
    d.add(String(x + 6, y - tab_h + 3.4, title, fontName=BODY_B, fontSize=7.2,
                 fillColor=NAVY))


def note(d, x, y, w, lines, fill=colors.HexColor("#FFFDE7")):
    h = 2 * PAD + len(lines) * (MEM_FS + 2)
    d.add(Polygon([x, y, x + w - 7, y, x + w, y - 7, x + w, y - h, x, y - h],
                  fillColor=fill, strokeColor=colors.HexColor("#C9A227"),
                  strokeWidth=0.6))
    row = y - PAD
    for line in lines:
        row -= MEM_FS + 2
        d.add(String(x + 5, row, line, fontName=BODY_I, fontSize=MEM_FS,
                     fillColor=colors.HexColor("#5A4A00")))
    return h


def fit(d, pad=6):
    """Crops a drawing to its content and centres it in the text frame."""
    x0, y0, x1, y1 = d.getBounds()
    g = Group(*d.contents)
    g.translate(-x0 + pad, -y0 + pad)
    out = Drawing(min(x1 - x0 + 2 * pad, USABLE), y1 - y0 + 2 * pad)
    out.add(g)
    out.hAlign = "CENTER"
    return out


def tree(d, parent, children, bus_y, kind="inherit"):
    """Classic UML generalisation tree: one trunk, one bus, one stub per child."""
    connect(d, [(parent.cx, bus_y), (parent.cx, parent.bottom)], kind)
    xs = [c.cx for c in children]
    d.add(Line(min(xs), bus_y, max(xs), bus_y, strokeColor=NAVY, strokeWidth=0.8))
    for child in children:
        d.add(Line(child.cx, child.y, child.cx, bus_y, strokeColor=NAVY,
                   strokeWidth=0.8))


def legend(d, x, y, w=124):
    rows = [("inherit", "generalisation"), ("realize", "realisation"),
            ("dep", "dependency / uses")]
    h = 13 + len(rows) * 13
    d.add(Rect(x, y - h, w, h, fillColor=colors.white, strokeColor=RULE,
               strokeWidth=0.6))
    d.add(String(x + 5, y - 10, "Legend", fontName=BODY_B, fontSize=6.6,
                 fillColor=NAVY))
    row = y - 23
    for kind, label in rows:
        connect(d, [(x + 5, row), (x + 34, row)], kind)
        d.add(String(x + 40, row - 2.2, label, fontName=BODY, fontSize=6.2,
                     fillColor=INK))
        row -= 13

# ---------------------------------------------------------------------------
# Figure 1 - responsibility / dependency overview (SRP)
# ---------------------------------------------------------------------------

def fig_layers():
    d = Drawing(USABLE, 330)
    main = Box(140, 325, 190, "main()", stereo="composition root",
               methods=["+ builds and injects every", "  concrete collaborator"],
               fill=colors.HexColor("#EDEDF3"))
    repo = Box(0, 250, 150, "AssetRepository", stereo="SRP: persistence",
               methods=["+ add(asset)", "+ list_all()"])
    calc = Box(160, 250, 150, "PortfolioCalculator", stereo="SRP: calculation",
               methods=["+ value_positions()", "+ net_worth()", "+ allocation_by_kind()"])
    exp = Box(320, 250, 150, "Csv / Json Exporter", stereo="SRP: reporting",
              methods=["+ export(positions, path)"])
    asset = Box(0, 135, 150, "Asset", stereo="abstract", abstract=True,
                fill=ABSTRACT_FILL, methods=["+ market_value(prices)*"])
    pp = Box(160, 135, 150, "PriceProvider", stereo="interface", abstract=True,
             fill=IFACE_FILL, methods=["+ get_price(symbol)*"])
    pos = Box(320, 135, 150, "Position", stereo="dataclass, frozen",
              attrs=["symbol, kind, quantity, value"])
    for b in (main, repo, calc, exp, asset, pp, pos):
        b.draw(d)

    y1 = 262
    for target, off in ((repo, -60), (calc, 0), (exp, 60)):
        connect(d, [(main.cx + off, main.bottom), (main.cx + off, y1),
                    (target.cx, y1), (target.cx, target.y)], "dep")
    y2 = 150
    connect(d, [(repo.cx, repo.bottom), (repo.cx, asset.y)], "dep",
            label="«persists»", label_at=(repo.cx + 36, 160))
    connect(d, [(calc.cx - 30, calc.bottom), (calc.cx - 30, y2),
                (asset.right, y2), (asset.right, asset.cy)], "dep",
            label="«values»", label_at=(calc.cx - 30, 168))
    connect(d, [(calc.cx + 30, calc.bottom), (calc.cx + 30, pp.y)], "dep",
            label="«asks price»", label_at=(calc.cx + 66, 160))
    connect(d, [(exp.cx, exp.bottom), (exp.cx, pos.y)], "dep",
            label="«reads»", label_at=(exp.cx + 30, 160))
    connect(d, [(calc.cx + 54, main.bottom - 4), (calc.cx + 54, 302),
                (pos.cx, 302), (pos.cx, pos.y)], "dep",
            label="«creates Position»", label_at=(pos.cx - 50, 306))
    note(d, 0, 325, 128, ["One box = one reason", "to change. Data crosses",
                          "the boundaries, never", "responsibilities."])
    return fit(d)


# ---------------------------------------------------------------------------
# Figure 2 - complete class diagram
# ---------------------------------------------------------------------------

def fig_classes():
    d = Drawing(USABLE, 645)
    repo = Box(0, 615, 152, "AssetRepository",
               attrs=["- conn: sqlite3.Connection"],
               methods=["+ add(asset)", "+ add_many(assets)",
                        "+ list_all(): List[Asset]", "- _to_asset(row): Asset"])
    calc = Box(166, 615, 152, "PortfolioCalculator",
               attrs=["- prices: PriceProvider"],
               methods=["+ value_positions(assets)", "+ net_worth(positions)",
                        "+ allocation_by_kind(pos)"])
    pos = Box(332, 615, 138, "Position", stereo="dataclass, frozen",
              attrs=["+ symbol: str", "+ kind: str", "+ quantity: Decimal",
                     "+ value: Decimal"])
    asset = Box(148, 505, 175, "Asset", stereo="abstract", abstract=True,
                fill=ABSTRACT_FILL,
                attrs=["+ symbol: str", "+ quantity: Decimal",
                       "+ kind: ClassVar[str]"],
                methods=["+ market_value(prices): Decimal*",
                         "+ details: Dict[str, str]", "+ from_details(...): Asset"])
    stock = Box(0, 380, 105, "Stock", attrs=["+ exchange: str"],
                methods=["+ market_value()"])
    crypto = Box(112, 380, 105, "Crypto", attrs=["+ wallet: str"],
                 methods=["+ market_value()"])
    cash = Box(224, 380, 105, "CashSavings", attrs=["+ annual_rate"],
               methods=["+ market_value()"])
    realestate = Box(336, 380, 105, "RealEstate",
                     attrs=["+ appraised_value", "+ mortgage_balance"],
                     methods=["+ market_value()"], fill=NEW_FILL)
    pp = Box(148, 295, 180, "PriceProvider", stereo="interface / ABC",
             abstract=True, fill=IFACE_FILL,
             methods=["+ get_price(symbol): Decimal*"])
    mock = Box(30, 225, 120, "MockPriceProvider", attrs=["- prices: Dict"],
               methods=["+ get_price()"])
    api = Box(165, 225, 120, "ApiPriceProvider",
              attrs=["- base_url: str", "- api_key: str"],
              methods=["+ get_price()"])
    caching = Box(300, 225, 140, "CachingPriceProvider",
                  attrs=["- inner: PriceProvider", "- cache: Dict"],
                  methods=["+ get_price()"])
    exp = Box(148, 140, 180, "PortfolioExporter", stereo="abstract",
              abstract=True, fill=ABSTRACT_FILL,
              methods=["+ export(positions, path)*"])
    csvx = Box(90, 70, 110, "CsvExporter", methods=["+ export()"])
    jsonx = Box(230, 70, 110, "JsonExporter", methods=["+ export()"])
    for b in (repo, calc, pos, asset, stock, crypto, cash, realestate,
              pp, mock, api, caching, exp, csvx, jsonx):
        b.draw(d)

    tree(d, asset, [stock, crypto, cash, realestate], 394)
    tree(d, pp, [mock, api, caching], 240, kind="realize")
    tree(d, exp, [csvx, jsonx], 83)

    connect(d, [(76, repo.bottom), (76, 457), (asset.x, 457)], "dep",
            label="«rebuilds»", label_at=(112, 462))
    connect(d, [(242, calc.bottom), (242, asset.y)], "dep",
            label="«values»", label_at=(272, 522))
    connect(d, [(calc.cx + 40, calc.y), (calc.cx + 40, 632), (pos.cx, 632),
                (pos.cx, pos.y)], "dep",
            label="«creates»", label_at=(pos.cx - 58, 635))
    connect(d, [(300, calc.bottom), (300, 528), (446, 528), (446, 273),
                (pp.right, 273)], "dep",
            label="«asks price»", label_at=(412, 534))
    connect(d, [(exp.right, exp.cy), (466, exp.cy), (466, pos.bottom)], "dep",
            label="«reads»", label_at=(400, 148))
    note(d, 0, 152, 140, ["Core classes are CLOSED for",
                          "modification. RealEstate (green)",
                          "was added in a later iteration."])
    legend(d, 344, 140, w=112)
    return fit(d)


# ---------------------------------------------------------------------------
# Figure 3 - OCP: extension without modification
# ---------------------------------------------------------------------------

def fig_ocp():
    d = Drawing(USABLE, 300)
    d.add(Rect(0, 150, 300, 140, fillColor=None,
               strokeColor=colors.HexColor("#8A8FA3"), strokeWidth=0.7,
               strokeDashArray=(3, 3)))
    d.add(String(6, 278, "closed for modification (never edited again)",
                 fontName=BODY_I, fontSize=6.8, fillColor=GREY))
    calc = Box(10, 270, 130, "PortfolioCalculator",
               methods=["for a in assets:", "  a.market_value(prices)",
                        "no isinstance(), no if/elif*"],
               fill=colors.HexColor("#EDEDF3"))
    asset = Box(160, 270, 130, "Asset", stereo="abstract", abstract=True,
                fill=ABSTRACT_FILL, methods=["+ market_value(prices)*"])
    stock = Box(0, 130, 88, "Stock", methods=["qty x price"])
    crypto = Box(95, 130, 88, "Crypto", methods=["qty x price"])
    cash = Box(190, 130, 95, "CashSavings", methods=["balance"])
    new = Box(300, 130, 170, "RealEstate", stereo="added in iteration 2",
              methods=["appraised - mortgage"], fill=NEW_FILL,
              tag="0 lines changed elsewhere")
    for b in (calc, asset, stock, crypto, cash, new):
        b.draw(d)
    connect(d, [(calc.right, calc.cy), (asset.x, calc.cy)], "dep",
            label="«depends only on»", label_at=(150, calc.cy + 6))
    tree(d, asset, [stock, crypto, cash, new], 162)
    note(d, 300, 290, 170, ["Open for extension: a new asset",
                            "type only adds a subclass and a",
                            "@register_asset decorator."])
    return fit(d)


# ---------------------------------------------------------------------------
# Figure 4 - DIP: the direction of the dependency is inverted
# ---------------------------------------------------------------------------

def fig_dip():
    d = Drawing(USABLE, 290)
    half = USABLE / 2.0
    d.add(Line(half, 10, half, 265, strokeColor=RULE, strokeWidth=0.7,
               strokeDashArray=(3, 3)))
    d.add(String(half / 2, 272, "(a) without DIP - rigid", fontName=BODY_B,
                 fontSize=8.4, fillColor=colors.HexColor("#A03030"),
                 textAnchor="middle"))
    d.add(String(half + half / 2, 272, "(b) with DIP - inverted",
                 fontName=BODY_B, fontSize=8.4,
                 fillColor=colors.HexColor("#1E7B34"), textAnchor="middle"))

    bad_calc = Box(half / 2 - 70, 255, 140, "PortfolioCalculator",
                   stereo="high-level policy", methods=["+ net_worth()"],
                   fill=colors.HexColor("#FBECEC"))
    bad_api = Box(half / 2 - 70, 140, 140, "ApiPriceProvider",
                  stereo="low-level detail", methods=["+ get_price() via HTTP"],
                  fill=colors.HexColor("#FBECEC"))
    bad_calc.draw(d)
    bad_api.draw(d)
    connect(d, [(bad_calc.cx, bad_calc.bottom), (bad_calc.cx, bad_api.y)], "assoc",
            label="imports / instantiates", label_at=(bad_calc.cx + 2, 128))
    note(d, 8, 95, half - 24,
         ["Policy cannot be tested or demoed without the",
          "network. Changing the HTTP client changes the",
          "calculator. The arrow points the wrong way."],
         fill=colors.HexColor("#FBECEC"))

    gx = half + 14
    gw = half - 28
    good_calc = Box(gx + gw / 2 - 70, 255, 140, "PortfolioCalculator",
                    stereo="high-level policy", methods=["+ net_worth()"],
                    fill=colors.HexColor("#EDF7EE"))
    iface = Box(gx + gw / 2 - 75, 185, 150, "PriceProvider",
                stereo="abstraction", abstract=True, fill=IFACE_FILL,
                methods=["+ get_price(symbol)*"])
    m1 = Box(gx, 110, 68, "Mock", methods=["dict"], fill=colors.white)
    m2 = Box(gx + 74, 110, 68, "Api", methods=["HTTP"], fill=colors.white)
    m3 = Box(gx + 148, 110, 74, "Caching", methods=["wraps"], fill=colors.white)
    for b in (good_calc, iface, m1, m2, m3):
        b.draw(d)
    connect(d, [(good_calc.cx, good_calc.bottom), (good_calc.cx, iface.y)], "dep",
            label="«uses»", label_at=(good_calc.cx + 26, 225))
    tree(d, iface, [m1, m2, m3], 130, kind="realize")
    note(d, gx - 6, 66, gw + 12,
         ["Both sides now depend on the abstraction.",
          "The demo injects Mock, production injects Api -",
          "the calculator is never recompiled."],
         fill=colors.HexColor("#EDF7EE"))
    return fit(d)


# ---------------------------------------------------------------------------
# Figure 5 - sequence diagram of one dashboard refresh
# ---------------------------------------------------------------------------

def fig_sequence():
    d = Drawing(USABLE, 360)
    lanes = [("main()", 42), ("repo:\nAssetRepository", 140),
             ("calc:\nPortfolioCalculator", 240), ("a:Asset", 330),
             ("p:PriceProvider", 400), ("exp:CsvExporter", 455)]
    xs = [38, 128, 232, 318, 384, 444]
    labels = ["main()", "repo :AssetRepository", "calc :PortfolioCalculator",
              "a :Asset", "p :PriceProvider", "exp :CsvExporter"]
    widths = [58, 96, 104, 54, 78, 80]
    top = 352
    for x, label, w in zip(xs, labels, widths):
        d.add(Rect(x - w / 2.0, top - 20, w, 20, fillColor=colors.HexColor("#EDEDF3"),
                   strokeColor=NAVY, strokeWidth=0.8))
        d.add(String(x, top - 13.5, label, fontName=BODY_B, fontSize=6.6,
                     fillColor=NAVY, textAnchor="middle"))
        d.add(Line(x, 18, x, top - 20, strokeColor=GREY, strokeWidth=0.6,
                   strokeDashArray=(2.5, 2.5)))

    d.add(Rect(292, 95, 160, 128, fillColor=None, strokeColor=colors.HexColor("#8A8FA3"),
               strokeWidth=0.7, strokeDashArray=(3, 3)))
    d.add(Rect(292, 211, 62, 12, fillColor=colors.HexColor("#EFEFF4"),
               strokeColor=colors.HexColor("#8A8FA3"), strokeWidth=0.7))
    d.add(String(296, 214.5, "loop [each asset]", fontName=BODY_I, fontSize=6.2,
                 fillColor=INK))

    msgs = [
        (0, 1, 305, "1: list_all()", "call"),
        (1, 0, 288, "2: List[Asset]", "ret"),
        (0, 2, 266, "3: value_positions(assets)", "call"),
        (2, 3, 200, "4: market_value(prices)", "call"),
        (3, 4, 175, "5: get_price(symbol)", "call"),
        (4, 3, 152, "6: Decimal", "ret"),
        (3, 2, 128, "7: Decimal", "ret"),
        (2, 0, 82, "8: List[Position]", "ret"),
        (0, 2, 60, "9: net_worth(positions)", "call"),
        (0, 5, 38, "10: export(positions, path)", "call"),
    ]
    for src, dst, y, text, kind in msgs:
        x0, x1 = xs[src], xs[dst]
        connect(d, [(x0, y), (x1, y)], "dep" if kind == "ret" else "assoc")
        mid = (x0 + x1) / 2.0
        d.add(String(mid, y + 3.6, text,
                     fontName=BODY_I if kind == "ret" else BODY,
                     fontSize=6.5, fillColor=INK if kind == "call" else GREY,
                     textAnchor="middle"))
    return fit(d)


FIGURES = [
    ("fig_layers", fig_layers),
    ("fig_classes", fig_classes),
    ("fig_ocp", fig_ocp),
    ("fig_dip", fig_dip),
    ("fig_sequence", fig_sequence),
]


def preview(outdir):
    """Renders every figure to SVG plus an HTML index, for visual checking."""
    from reportlab.graphics import renderSVG
    parts = []
    for name, builder in FIGURES:
        path = os.path.join(outdir, name + ".svg")
        renderSVG.drawToFile(builder(), path)
        parts.append(
            "<h2>%s</h2><div class='fig'>%s</div>"
            % (name, open(path, encoding="utf-8").read().split("?>", 1)[-1]))
    html = ("<!doctype html><meta charset='utf-8'><style>"
            "body{font:14px Arial;background:#fff;margin:24px;max-width:720px}"
            "h2{color:#1F3864;font-size:15px;margin:26px 0 6px}"
            "svg{border:1px solid #ddd}</style>" + "".join(parts))
    index = os.path.join(outdir, "figures.html")
    open(index, "w", encoding="utf-8").write(html)
    print(index)


# ---------------------------------------------------------------------------
# Document scaffolding
# ---------------------------------------------------------------------------

FIG = {}  # figure key -> "4.1" etc., filled while the story is assembled


class ReportDoc(BaseDocTemplate):
    """Adds TOC notifications and the page furniture."""

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            name = flowable.style.name
            if name in ("h1", "h2"):
                self.notify("TOCEntry",
                            (0 if name == "h1" else 1,
                             flowable.getPlainText(), self.page))

    def handle_pageBegin(self):
        BaseDocTemplate.handle_pageBegin(self)


def body_page(canvas, doc):
    canvas.saveState()
    canvas.setFont(BODY, 8)
    canvas.setFillColor(GREY)
    canvas.drawString(MARGIN, PAGE_H - MARGIN + 14,
                      "UTM – FCIM – %s" % COVER["discipline"])
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
    canvas.rect(MARGIN - 14, MARGIN - 14, PAGE_W - 2 * MARGIN + 28,
                PAGE_H - 2 * MARGIN + 28)
    canvas.restoreState()


def find_logo():
    for pattern in ("utm_logo.*", "logo.*", "utm*.png", "utm*.jpg"):
        hits = sorted(glob.glob(os.path.join(HERE, pattern)))
        if hits:
            return hits[0]
    return None


def cover_story():
    out = []
    logo = find_logo()
    if logo:
        img = Image(logo, width=4.92 * cm, height=2.54 * cm)
        img.hAlign = "CENTER"
        out += [Spacer(1, 6), img, Spacer(1, 14)]
    else:
        out += [Spacer(1, 26)]
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
        Spacer(1, 2.6 * cm),
    ]
    checked = Table([[Paragraph("Checked by:<br/>%s<br/>FCIM, UTM" % COVER["professor"],
                                S["cover_right"])]],
                    colWidths=[6.5 * cm])
    checked.hAlign = "RIGHT"
    out += [checked, Spacer(1, 1.6 * cm), P(COVER["city_year"], "cover_small")]
    return out


def figure(drawing, number, caption, key=None):
    if key:
        FIG[key] = number
    return KeepTogether([drawing,
                         P("Figure %s – %s" % (number, caption), "caption")])


def toc_story():
    toc = TableOfContents()
    toc.levelStyles = [S["toc1"], S["toc2"]]
    return [P("Contents", "h1_notoc"), toc]


# ---------------------------------------------------------------------------
# Report body
# ---------------------------------------------------------------------------

CONSOLE_OUTPUT = """
$ python3 wealth_dashboard.py
PERSONAL WEALTH DASHBOARD
----------------------------------------------
AAPL             stock              2,574.00
MSFT             stock              2,160.50
BTC              crypto            21,437.50
ETH              crypto            12,519.15
EUR-SAVINGS      cash               7,500.00
FLAT-CHISINAU    real_estate       44,000.00
----------------------------------------------
NET WORTH                            90,191.15

Allocation by asset class
  real_estate     48.79%
  crypto          37.65%
  cash             8.32%
  stock            5.25%

Exported: portfolio.csv, portfolio.json
"""

CSV_OUTPUT = """
symbol,kind,quantity,value
AAPL,stock,12,2574.00
MSFT,stock,5,2160.50
BTC,crypto,0.35,21437.50
ETH,crypto,4.2,12519.15
EUR-SAVINGS,cash,7500,7500.00
FLAT-CHISINAU,real_estate,1,44000.00
"""

CODE_DIP = """
class PriceProvider(ABC):
    \"\"\"Abstraction: 'something that can tell me the price of a symbol'.\"\"\"

    @abstractmethod
    def get_price(self, symbol: str) -> Decimal:
        raise NotImplementedError


class MockPriceProvider(PriceProvider):
    \"\"\"DIP in action: deterministic prices. Safe for the live class demo.\"\"\"

    def __init__(self, prices: Dict[str, Decimal]):
        self._prices = prices

    def get_price(self, symbol: str) -> Decimal:
        if symbol not in self._prices:
            raise KeyError("No mock price configured for %r" % symbol)
        return self._prices[symbol]
"""

CODE_INJECT = """
class PortfolioCalculator:
    def __init__(self, prices: PriceProvider):   # <- injected, not constructed
        self._prices = prices

# composition root - the only place that names concrete classes
def demo_prices() -> PriceProvider:
    return CachingPriceProvider(MockPriceProvider({...}))   # demo
    # return ApiPriceProvider(base_url, api_key)            # production
"""

CODE_ASSET = """
@dataclass
class Asset(ABC):
    symbol: str
    quantity: Decimal
    kind: ClassVar[str] = "asset"

    @abstractmethod
    def market_value(self, prices: PriceProvider) -> Decimal:
        \"\"\"Current value of this holding. Subclasses decide *how*.\"\"\"
        raise NotImplementedError


@register_asset
@dataclass
class CashSavings(Asset):
    kind: ClassVar[str] = "cash"
    annual_rate: Decimal = Decimal("0")

    def market_value(self, prices: PriceProvider) -> Decimal:
        return self.quantity        # cash ignores the price provider entirely
"""

CODE_CALC = """
def value_positions(self, assets: Iterable[Asset]) -> List[Position]:
    # No isinstance() checks and no if/elif chain over asset types: each
    # asset values itself (polymorphism is what makes OCP possible).
    return [
        Position(
            symbol=asset.symbol,
            kind=asset.kind,
            quantity=asset.quantity,
            value=money(asset.market_value(self._prices)),
        )
        for asset in assets
    ]
"""

CODE_NEW = """
@register_asset
@dataclass
class RealEstate(Asset):
    kind: ClassVar[str] = "real_estate"
    appraised_value: Decimal = Decimal("0")
    mortgage_balance: Decimal = Decimal("0")

    def market_value(self, prices: PriceProvider) -> Decimal:
        # Equity, not gross value - a valuation rule unique to this type.
        return (self.appraised_value - self.mortgage_balance) * self.quantity
"""

CODE_REPO = """
@staticmethod
def _to_asset(row: Sequence[str]) -> Asset:
    # OCP: the repository never names Stock/Crypto/Cash - it looks the class
    # up in the registry and lets the class rebuild itself.
    kind, symbol, quantity, details = row
    asset_cls = ASSET_REGISTRY.get(kind)
    if asset_cls is None:
        raise ValueError("Unknown asset kind in database: %r" % kind)
    return asset_cls.from_details(symbol, quantity, json.loads(details))
"""

CODE_FROM_DETAILS = """
@classmethod
def from_details(cls, symbol, quantity, details):
    kwargs = {}
    for field in dataclass_fields(cls):
        if field.name in details:
            raw = details[field.name]
            kwargs[field.name] = Decimal(raw) if "Decimal" in str(field.type) else raw
    return cls(symbol=symbol, quantity=Decimal(quantity), **kwargs)
"""


def content_story():
    st = []
    st += [P("1   Purpose of the Work", "h1")]
    st += [P(
        "The purpose of this laboratory work is to design and implement a small but "
        "complete application whose structure is driven by the SOLID principles, and to "
        "demonstrate that those principles produce measurable, verifiable properties of "
        "the code rather than stylistic preferences. The chosen domain is a "
        "<b>Personal Wealth Dashboard and Multi-Asset Portfolio Tracker</b>: an "
        "application that computes a user's total net worth across stocks, "
        "cryptocurrencies and cash savings.")]
    st += [P("The concrete objectives were:")]
    st += bullets([
        "to separate persistence, financial calculation and reporting so that each class "
        "has exactly one reason to change (<b>Single-Responsibility Principle</b>);",
        "to make the set of supported asset types extensible without editing the "
        "valuation logic (<b>Open/Closed Principle</b>);",
        "to invert the dependency on the market-data source so that a deterministic "
        "provider can be substituted for a live API at run time "
        "(<b>Dependency Inversion Principle</b>);",
        "to document the resulting architecture with UML class and sequence diagrams and "
        "to verify the design by extending the system with a new asset type.",
    ])
    st += [P(
        "The implementation is a single Python 3 module, "
        "<font name='Courier'>wealth_dashboard.py</font> (449 lines), which depends only "
        "on the standard library and runs with "
        "<font name='Courier'>python3 wealth_dashboard.py</font>. The complete source is "
        "reproduced in Appendix A.")]

    st += [P("2   Theoretical Background", "h1")]
    st += [P(
        "SOLID is the acronym introduced by Robert C. Martin for five principles of "
        "object-oriented design [1]. Table 2.1 summarises all five; the three that this "
        "work implements explicitly are discussed in detail below.")]
    st += [data_table([
        ["Principle", "Statement", "Role in this work"],
        ["SRP", "A class should have only one reason to change.",
         "Implemented: three separate classes for storage, calculation and export."],
        ["OCP", "Software entities should be open for extension but closed for modification.",
         "Implemented: the <font name='Courier'>Asset</font> hierarchy and the asset registry."],
        ["LSP", "Subtypes must be substitutable for their base types.",
         "Respected: every asset honours the same contract (section 7)."],
        ["ISP", "Clients should not depend on methods they do not use.",
         "Respected: the interfaces declare a single method each."],
        ["DIP", "Depend on abstractions, not on concretions.",
         "Implemented: <font name='Courier'>PriceProvider</font> is injected into the calculator."],
    ], [1.6 * cm, 6.1 * cm, 6.5 * cm])]
    st += [P("Table 2.1 – The five SOLID principles and their role in the project",
             "caption")]

    st += [P("2.1   Single-Responsibility Principle", "h2")]
    st += [P(
        "A module should be responsible to one, and only one, actor. The practical test is "
        "the question “for what reason would this file have to be edited?” If more "
        "than one answer exists – for example “because the database schema changed” "
        "and “because the report must now be produced in JSON” – the module "
        "carries more than one responsibility and the two reasons will eventually "
        "interfere with each other.")]

    st += [P("2.2   Open/Closed Principle", "h2")]
    st += [P(
        "Formulated by Bertrand Meyer [5], the principle requires that the behaviour of a "
        "module can be extended without modifying its source. In a dynamically typed "
        "language the mechanism is polymorphism: the client calls an operation declared by "
        "an abstraction, and each new subtype supplies its own implementation. The "
        "diagnostic symptom of a violation is a chain of "
        "<font name='Courier'>if</font>/<font name='Courier'>elif</font> or "
        "<font name='Courier'>isinstance()</font> tests over a type tag, because such a "
        "chain must be reopened and edited for every new type.")]

    st += [P("2.3   Dependency Inversion Principle", "h2")]
    st += [P(
        "High-level modules should not depend on low-level modules; both should depend on "
        "abstractions. In a naive layering, the policy that computes net worth would "
        "import an HTTP client in order to read quotes, which makes the policy untestable "
        "offline and couples it to a vendor. Inverting the dependency means declaring the "
        "abstraction next to the policy and letting the detail implement it; the concrete "
        "object is then supplied from outside, a technique known as dependency injection.")]

    st += [P("3   Application Domain and Requirements", "h1")]
    st += [P(
        "The application aggregates holdings of different natures into a single figure. "
        "Three properties of the domain shaped the design:")]
    st += bullets([
        "<b>heterogeneous valuation.</b> A stock or a crypto holding is valued as "
        "quantity multiplied by a live unit price; a savings account is worth its balance "
        "and needs no market data at all; real estate is valued as appraised value minus "
        "the outstanding mortgage. A single formula cannot cover these cases;",
        "<b>an open set of asset types.</b> Bonds, pension funds or vehicles are plausible "
        "future additions, and adding one must not endanger the already-tested valuation "
        "of the existing types;",
        "<b>an unreliable, external data source.</b> Live quotes come from a third-party "
        "API over the network, which is unavailable during a classroom demonstration and "
        "unsuitable for deterministic testing.",
    ])
    st += [P(
        "Monetary values are represented with "
        "<font name='Courier'>decimal.Decimal</font> rather than "
        "<font name='Courier'>float</font>, because binary floating point cannot represent "
        "decimal fractions such as 0.10 exactly and accumulates error over sums; "
        "quantities are stored in SQLite as text for the same reason.")]
    return st


def architecture_story():
    st = [P("4   Architecture of the Solution", "h1")]
    st += [P(
        "The system is organised as four groups of classes: a persistence group, a "
        "calculation group, a reporting group, and the abstractions that connect them. "
        "Figure 4.1 shows the responsibilities and the direction of the dependencies; no "
        "arrow points from an abstraction towards a concrete class, and no arrow connects "
        "two responsibility groups directly – they communicate only through the data "
        "objects they exchange.")]
    st += [figure(fig_layers(), "4.1",
                  "Responsibility split and dependency directions (SRP overview)")]
    st += [P(
        "Figure 4.2 is the complete class diagram. The three abstractions "
        "(<font name='Courier'>Asset</font>, <font name='Courier'>PriceProvider</font>, "
        "<font name='Courier'>PortfolioExporter</font>) each sit above a family of "
        "interchangeable implementations, and every concrete class below them can be "
        "replaced or supplemented without touching the classes above. "
        "<font name='Courier'>CachingPriceProvider</font> is both a realisation of "
        "<font name='Courier'>PriceProvider</font> and a holder of one: it is the "
        "<i>Decorator</i> pattern [3], which adds caching by composition instead of by "
        "editing the providers it wraps.")]
    st += [PageBreak(), figure(fig_classes(), "4.2",
                               "Complete class diagram of the portfolio tracker")]
    st += [P(
        "Figure 4.3 traces one refresh of the dashboard. The essential detail is message "
        "5: the price lookup is issued by the asset against the injected abstraction, so "
        "the calculator never learns where prices come from, and the assets that do not "
        "need a price (cash, real estate) simply never send that message.")]
    st += [figure(fig_sequence(), "4.3",
                  "Sequence of one dashboard refresh, from main() to the exported file")]
    return st


def implementation_story():
    st = [P("5   Implementation", "h1")]

    st += [P("5.1   Single-Responsibility Principle", "h2")]
    st += [P(
        "Three classes divide the work. <font name='Courier'>AssetRepository</font> owns "
        "the SQLite connection, the schema and the two conversions between rows and "
        "objects; it performs no arithmetic. <font name='Courier'>PortfolioCalculator</font> "
        "performs only arithmetic; it contains no SQL and no file access. "
        "<font name='Courier'>CsvExporter</font> and <font name='Courier'>JsonExporter</font> "
        "only serialise. The glue between them is "
        "<font name='Courier'>Position</font>, a frozen dataclass that is the calculator's "
        "output and the exporter's input, which is what allows the exporters to remain "
        "ignorant of both the database and the asset hierarchy.")]
    st += [data_table([
        ["Class", "Single responsibility", "Changes when…"],
        ["<font name='Courier'>AssetRepository</font>", "Storing and retrieving assets",
         "the storage technology or schema changes"],
        ["<font name='Courier'>PortfolioCalculator</font>", "Valuing a portfolio",
         "a valuation or allocation rule changes"],
        ["<font name='Courier'>CsvExporter</font> / <font name='Courier'>JsonExporter</font>",
         "Serialising a report", "an output format changes"],
        ["<font name='Courier'>Position</font>", "Carrying one valued holding",
         "the reported fields change"],
    ], [4.3 * cm, 4.9 * cm, 5.0 * cm])]
    st += [P("Table 5.1 – One reason to change per class", "caption")]

    st += [P("5.2   Open/Closed Principle", "h2")]
    st += [P(
        "<font name='Courier'>Asset</font> is an abstract base class that declares "
        "<font name='Courier'>market_value()</font>. Each concrete asset implements its own "
        "valuation rule, including the degenerate one: "
        "<font name='Courier'>CashSavings</font> ignores the price provider and returns its "
        "balance.")]
    st += [listing(CODE_ASSET)]
    st += [P("Listing 5.1 – The Asset abstraction and one implementation", "caption")]
    st += [P(
        "The calculator consumes that abstraction. The property that matters is a negative "
        "one – the absence of any type test:")]
    st += [listing(CODE_CALC)]
    st += [P("Listing 5.2 – Valuation without a single type test", "caption")]
    st += [P(
        "The principle was then verified experimentally. After the system was complete and "
        "running, a fourth asset type was added:")]
    st += [listing(CODE_NEW)]
    st += [P("Listing 5.3 – The extension used to verify the Open/Closed Principle",
             "caption")]
    st += [P(
        "Adding <font name='Courier'>RealEstate</font> required <b>no modification</b> of "
        "<font name='Courier'>PortfolioCalculator</font>, "
        "<font name='Courier'>AssetRepository</font>, either exporter, or any existing "
        "asset class; the net worth in section 6 includes it. Figure 5.1 states the "
        "relationship that makes this possible.")]
    st += [figure(fig_ocp(), "5.1",
                  "Extension without modification: the core depends only on Asset")]
    st += [P(
        "Persistence is open in the same way. Asset classes register themselves with a "
        "decorator, and the repository resolves the stored type tag through that registry "
        "instead of naming the classes:")]
    st += [listing(CODE_REPO)]
    st += [P("Listing 5.4 – Type-agnostic reconstruction through the registry",
             "caption")]
    st += [P(
        "A subtlety appears here. Extra fields are persisted as JSON, so a new type with "
        "new <font name='Courier'>Decimal</font> fields would be restored as strings and "
        "would fail on arithmetic. Rather than maintaining a list of such fields in the "
        "repository – which would have to be edited for every new type, defeating the "
        "principle – each class rebuilds itself by reading its own dataclass "
        "annotations:")]
    st += [listing(CODE_FROM_DETAILS)]
    st += [P("Listing 5.5 – Type-driven reconstruction, so new fields need no registry edit",
             "caption")]

    st += [P("5.3   Dependency Inversion Principle", "h2")]
    st += [P(
        "The calculator must not depend on an HTTP client. The abstraction is therefore "
        "declared independently of any implementation, and two implementations are provided:")]
    st += [listing(CODE_DIP)]
    st += [P("Listing 5.6 – The PriceProvider abstraction and its test double", "caption")]
    st += [P(
        "The concrete provider is passed to the constructor, and only the composition root "
        "names concrete classes. Switching the entire application from mock data to a live "
        "feed is a one-line change in that function:")]
    st += [listing(CODE_INJECT)]
    st += [P("Listing 5.7 – Injection at the composition root", "caption")]
    st += [P(
        "Figure 5.2 contrasts the two arrangements. In (a) the high-level policy points at "
        "a low-level detail; in (b) both point at the abstraction, which is the inversion "
        "the principle is named after.")]
    st += [figure(fig_dip(), "5.2",
                  "The dependency before and after inversion")]
    st += [P(
        "The arrangement also pays off immediately: "
        "<font name='Courier'>CachingPriceProvider</font> adds request caching by wrapping "
        "any other provider, so a future rate limit on the live API can be absorbed without "
        "editing either the calculator or the API client.")]
    return st


def results_story():
    st = [P("6   Results", "h1")]
    st += [P(
        "The program was executed on macOS with CPython 3.9.6 and no third-party packages "
        "installed. The demo portfolio contains six holdings of four different asset "
        "types, priced by <font name='Courier'>MockPriceProvider</font>:")]
    st += [listing(CONSOLE_OUTPUT)]
    st += [P("Listing 6.1 – Program output", "caption")]
    st += [P("Table 6.1 reproduces the computed valuation.")]
    st += [data_table([
        ["Symbol", "Asset class", "Quantity", "Unit price", "Value (EUR)"],
        ["AAPL", "stock", "12", "214.50", "2,574.00"],
        ["MSFT", "stock", "5", "432.10", "2,160.50"],
        ["BTC", "crypto", "0.35", "61,250.00", "21,437.50"],
        ["ETH", "crypto", "4.2", "2,980.75", "12,519.15"],
        ["EUR-SAVINGS", "cash", "7,500", "–", "7,500.00"],
        ["FLAT-CHISINAU", "real_estate", "1", "85,000 − 41,000", "44,000.00"],
        ["<b>Total</b>", "", "", "", "<b>90,191.15</b>"],
    ], [3.3 * cm, 2.6 * cm, 2.2 * cm, 3.4 * cm, 2.7 * cm])]
    st += [P("Table 6.1 – Valuation of the demo portfolio", "caption")]
    st += [P(
        "Both exporters ran over the same list of "
        "<font name='Courier'>Position</font> objects and produced "
        "<font name='Courier'>portfolio.csv</font> and "
        "<font name='Courier'>portfolio.json</font>:")]
    st += [listing(CSV_OUTPUT)]
    st += [P("Listing 6.2 – portfolio.csv as produced by CsvExporter", "caption")]
    st += [P(
        "The real-estate row is the experimental result that matters: its value, "
        "44,000.00, is equity (85,000 appraised minus a 41,000 mortgage), it was computed "
        "by a class written after the calculator was finished, it survived a round trip "
        "through the database with its <font name='Courier'>Decimal</font> fields intact, "
        "and it was exported by an exporter that has never heard of real estate.")]

    st = st + [P("7   Discussion", "h1")]
    st += [P("7.1   Observed benefits", "h2")]
    st += bullets([
        "<b>Extension cost.</b> Adding a fourth asset type cost one class of eleven lines "
        "and one decorator; no existing class was edited, so no existing behaviour could "
        "regress.",
        "<b>Testability.</b> Because prices arrive through an injected abstraction, the "
        "valuation logic is fully exercisable offline and deterministically, which is also "
        "what makes the classroom demonstration independent of the network.",
        "<b>Locality of change.</b> A new output format touches one class; a change of "
        "database touches one class; a change of valuation rule touches one class.",
    ])
    st += [P("7.2   Limitations and trade-offs", "h2")]
    st += bullets([
        "<font name='Courier'>Asset.details</font> means a domain object knows which of "
        "its fields are persisted, a small concession of the Single-Responsibility "
        "Principle. The purer alternative – a separate mapper class per asset type "
        "– was rejected because it would require writing and registering a mapper for "
        "every new type, weakening the Open/Closed Principle that the design prioritises. "
        "The trade-off is deliberate.",
        "The allocation percentages in Listing 6.1 sum to 100.01% because each percentage "
        "is rounded to two decimals independently; presenting exact figures would require "
        "a largest-remainder adjustment.",
        "<font name='Courier'>ApiPriceProvider</font> is a stub. Supplying a live feed is "
        "precisely the extension the architecture was designed to absorb, but it has not "
        "been exercised against a real endpoint.",
        "The repository reads every asset into memory; for a portfolio of realistic size "
        "this is adequate, but aggregation would eventually belong in SQL.",
    ])
    st += [P("7.3   The remaining two principles", "h2")]
    st += [P(
        "Although not the focus of the work, the other two principles are observable in "
        "the result. <b>Liskov substitution</b> holds because every "
        "<font name='Courier'>Asset</font> subclass honours the same contract – "
        "<font name='Courier'>market_value()</font> returns a value for any valid holding "
        "and raises nothing – which is exactly why "
        "<font name='Courier'>CashSavings</font> ignoring its argument is safe rather than "
        "a violation. <b>Interface segregation</b> holds because the two interfaces declare "
        "one method each, so no implementation is forced to supply behaviour it does not "
        "need; <font name='Courier'>MockPriceProvider</font> is complete in three lines.")]

    st += [P("8   Conclusions", "h1")]
    st += [P(
        "A functioning multi-asset portfolio tracker was implemented in a single Python "
        "module and structured according to three SOLID principles. The Single-"
        "Responsibility Principle was applied by splitting persistence, calculation and "
        "reporting into classes with one reason to change each, communicating through an "
        "immutable data object. The Open/Closed Principle was applied through an abstract "
        "<font name='Courier'>Asset</font> class and a self-registering type registry, and "
        "was then verified empirically: a fourth asset type with an entirely different "
        "valuation rule was added without modifying any existing class. The Dependency "
        "Inversion Principle was applied by declaring the "
        "<font name='Courier'>PriceProvider</font> abstraction next to the policy that "
        "needs it and injecting the implementation from the composition root, which makes "
        "the system demonstrable offline and the live API a drop-in replacement.")]
    st += [P(
        "The main lesson of the work is that these principles are verifiable rather than "
        "decorative. The Open/Closed Principle predicted that a new asset type would cost "
        "nothing elsewhere, and the prediction was tested by making the change and "
        "observing that the diff touched no existing class. The design also showed where "
        "principles compete: persisting type-specific fields forced a choice between a "
        "purer separation of responsibilities and a cheaper extension path, and the "
        "resolution was an explicit trade-off rather than an oversight.")]

    st += [P("9   References", "h1")]
    refs = [
        "Martin, R. C. <i>Agile Software Development: Principles, Patterns, and "
        "Practices.</i> Prentice Hall, 2003.",
        "Martin, R. C. <i>Clean Architecture: A Craftsman's Guide to Software Structure "
        "and Design.</i> Prentice Hall, 2017.",
        "Gamma, E., Helm, R., Johnson, R., Vlissides, J. <i>Design Patterns: Elements of "
        "Reusable Object-Oriented Software.</i> Addison-Wesley, 1994.",
        "Liskov, B. “Data Abstraction and Hierarchy.” <i>ACM SIGPLAN Notices</i>, "
        "23(5), 1988.",
        "Meyer, B. <i>Object-Oriented Software Construction.</i> Prentice Hall, 1988.",
        "Python Software Foundation. <i>The Python Standard Library</i> – "
        "<font name='Courier'>abc</font>, <font name='Courier'>dataclasses</font>, "
        "<font name='Courier'>decimal</font>, <font name='Courier'>sqlite3</font>. "
        "https://docs.python.org/3/library/",
    ]
    st += [Paragraph("[%d]&nbsp;&nbsp;%s" % (i + 1, t), S["bullet"])
           for i, t in enumerate(refs)]
    return st


def appendix_story():
    st = [PageBreak(), P("Appendix A   Complete Source Code", "h1")]
    st += [P(
        "<font name='Courier'>wealth_dashboard.py</font> in full, as executed to produce "
        "the results in section 6. Line numbers are added for reference.")]
    with open(SOURCE_FILE, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    numbered = ["%3d  %s" % (i + 1, line) for i, line in enumerate(lines)]
    chunk = 62
    for start in range(0, len(numbered), chunk):
        st.append(listing("\n".join(numbered[start:start + chunk]), fs="code_sm"))
        st.append(Spacer(1, 4))
    return st


def build():
    doc = ReportDoc(OUTPUT_FILE, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                    topMargin=MARGIN, bottomMargin=MARGIN,
                    title="Laboratory Work No. %s – %s" % (COVER["lab_no"],
                                                                COVER["topic"]),
                    author=COVER["student"])
    frame = Frame(MARGIN, MARGIN, USABLE, PAGE_H - 2 * MARGIN, id="body")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame], onPage=cover_page),
        PageTemplate(id="body", frames=[frame], onPage=body_page),
    ])
    story = cover_story()
    story += [NextPageTemplate("body"), PageBreak()]
    story += toc_story()
    story += [PageBreak()]
    story += content_story()
    story += architecture_story()
    story += implementation_story()
    story += results_story()
    story += appendix_story()
    doc.multiBuild(story)
    print("wrote %s" % OUTPUT_FILE)


if __name__ == "__main__":
    import sys
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
    else:
        build()
