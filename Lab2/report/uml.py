"""UML drawing toolkit: classifier boxes, connectors, notes, trees, sequences."""

from reportlab.graphics.shapes import (Drawing, Group, Line, Polygon, PolyLine,
                                       Rect, String)
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

from styles import (ABSTRACT_FILL, BODY, BODY_B, BODY_I, CONCRETE_FILL, GREY,
                    IFACE_FILL, INK, NAVY, NEW_FILL, PKG_FILL, RULE, USABLE)

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
    kind: inherit | realize | dep | assoc | compose | aggregate | plain
    """
    flat = [c for pt in pts for c in pt]
    dash = (2.2, 2.2) if kind in ("realize", "dep") else None
    d.add(PolyLine(flat, strokeColor=NAVY, strokeWidth=0.8, strokeDashArray=dash))
    tail, head = pts[-2], pts[-1]
    if kind in ("inherit", "realize"):
        _triangle(d, tail, head)
    elif kind in ("dep", "assoc"):
        _open_arrow(d, tail, head)
    elif kind in ("compose", "aggregate"):
        _diamond(d, pts[0], pts[1], fill=NAVY if kind == "compose" else colors.white)
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
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    s = min(1.0, USABLE / w)  # scale down rather than crop a wide drawing
    g = Group(*d.contents)
    g.transform = (s, 0, 0, s, (pad - x0) * s, (pad - y0) * s)
    out = Drawing(w * s, h * s)
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
# Lab 2 additions
# ---------------------------------------------------------------------------

def tab_box(d, x, y, w, name, lines, fill=PKG_FILL, stereo=None):
    """UML package: a tab sitting on top of a box that lists its modules."""
    tab_w = min(w * 0.4, 70)
    d.add(Rect(x, y, tab_w, 10, fillColor=fill, strokeColor=NAVY, strokeWidth=0.8))
    box = Box(x, y, w, name, stereo=stereo, methods=lines, fill=fill)
    box.draw(d)
    return box


def fan(d, parent, children, bus_y, kind="dep", label=None):
    """One source, several targets: trunk, bus, one arrow per target."""
    dash = (2.2, 2.2) if kind in ("dep", "realize") else None
    d.add(Line(parent.cx, parent.bottom, parent.cx, bus_y, strokeColor=NAVY,
               strokeWidth=0.8, strokeDashArray=dash))
    xs = [c.cx for c in children] + [parent.cx]
    d.add(Line(min(xs), bus_y, max(xs), bus_y, strokeColor=NAVY, strokeWidth=0.8,
               strokeDashArray=dash))
    for child in children:
        connect(d, [(child.cx, bus_y), (child.cx, child.y)], kind)
    if label:
        d.add(String(parent.cx + 4, (parent.bottom + bus_y) / 2.0 - 2, label,
                     fontName=BODY_I, fontSize=6.6, fillColor=GREY))


def fan_in(d, sources, target, bus_y, kind="dep"):
    """Several sources, one target."""
    dash = (2.2, 2.2) if kind in ("dep", "realize") else None
    for source in sources:
        d.add(Line(source.cx, source.bottom, source.cx, bus_y, strokeColor=NAVY,
                   strokeWidth=0.8, strokeDashArray=dash))
    xs = [s.cx for s in sources] + [target.cx]
    d.add(Line(min(xs), bus_y, max(xs), bus_y, strokeColor=NAVY, strokeWidth=0.8,
               strokeDashArray=dash))
    connect(d, [(target.cx, bus_y), (target.cx, target.y)], kind)


def caption_text(d, x, y, text, size=7.6, anchor="start", bold=True, color=NAVY):
    d.add(String(x, y, text, fontName=BODY_B if bold else BODY_I, fontSize=size,
                 fillColor=color, textAnchor=anchor))


def sequence(d, labels, messages, top, step=20, frames=(), width=USABLE,
             head_fill=colors.HexColor("#EDEDF3")):
    """
    A sequence diagram. `messages` are (src, dst, text, kind) with kind
    "call" or "ret"; `frames` are (label, first_msg, last_msg, lane_a, lane_b).
    Lanes are spaced so the header boxes never overlap.
    """
    fs = 6.6
    widths = [stringWidth(t, BODY_B, fs) + 12 for t in labels]
    gap = (width - sum(widths)) / float(max(len(labels) - 1, 1))
    xs, cursor = [], 0.0
    for w in widths:
        xs.append(cursor + w / 2.0)
        cursor += w + gap
    ys = [top - 38 - i * step for i in range(len(messages))]
    bottom = ys[-1] - 14 if ys else top - 60
    for x, label, w in zip(xs, labels, widths):
        d.add(Rect(x - w / 2.0, top - 20, w, 20, fillColor=head_fill,
                   strokeColor=NAVY, strokeWidth=0.8))
        d.add(String(x, top - 13.5, label, fontName=BODY_B, fontSize=fs,
                     fillColor=NAVY, textAnchor="middle"))
        d.add(Line(x, bottom, x, top - 20, strokeColor=GREY, strokeWidth=0.6,
                   strokeDashArray=(2.5, 2.5)))
    for label, first, last, lane_a, lane_b in frames:
        x0 = xs[lane_a] - 16
        x1 = xs[lane_b] + 16
        y_top = ys[first] + 15
        y_bot = ys[last] - 7
        d.add(Rect(x0, y_bot, x1 - x0, y_top - y_bot, fillColor=None,
                   strokeColor=colors.HexColor("#8A8FA3"), strokeWidth=0.7,
                   strokeDashArray=(3, 3)))
        tw = stringWidth(label, BODY_I, 6.2) + 8
        d.add(Rect(x0, y_top - 11, tw, 11, fillColor=colors.HexColor("#EFEFF4"),
                   strokeColor=colors.HexColor("#8A8FA3"), strokeWidth=0.7))
        d.add(String(x0 + 4, y_top - 8, label, fontName=BODY_I, fontSize=6.2,
                     fillColor=INK))
    for (src, dst, text, kind), y in zip(messages, ys):
        connect(d, [(xs[src], y), (xs[dst], y)], "dep" if kind == "ret" else "assoc")
        d.add(String((xs[src] + xs[dst]) / 2.0, y + 3.6, text,
                     fontName=BODY_I if kind == "ret" else BODY, fontSize=6.5,
                     fillColor=GREY if kind == "ret" else INK, textAnchor="middle"))
    return xs, ys
