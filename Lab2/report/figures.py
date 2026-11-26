"""The UML figures of the Lab 2 report. Values are computed from the real code."""

import os
import sys

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors

from styles import (ABSTRACT_FILL, BODY, BODY_B, BODY_I, GREY, IFACE_FILL, INK,
                    NAVY, NEW_FILL, RULE, USABLE)
from uml import (Box, caption_text, connect, fan, fan_in, fit, note, sequence,
                 tab_box, tree)

LAB2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LAB2 not in sys.path:
    sys.path.insert(0, LAB2)

from wealth.assets import AssetGroup, PortfolioDirector  # noqa: E402
from wealth.money import money  # noqa: E402
from wealth.pricing import DemoMarketData  # noqa: E402
from wealth.valuation import FixedFee, PercentageFee  # noqa: E402

CLIENT_FILL = colors.HexColor("#EDEDF3")
FACADE_FILL = colors.HexColor("#E6F0FA")
SINGLETON_FILL = colors.HexColor("#EAF4EC")
CREATION_FILL = colors.HexColor("#FFF8E6")


def amount(value):
    return "{:,}".format(money(value))


def demo_tree():
    return PortfolioDirector().demo_portfolio(), DemoMarketData().provider()


# ---------------------------------------------------------------------------
# 4.1  Package structure
# ---------------------------------------------------------------------------

def fig_packages():
    d = Drawing(USABLE, 600)
    client = Box(160, 590, 150, "main.py", stereo="client",
                 methods=["uses WealthDashboard", "and PortfolioDirector only"],
                 fill=CLIENT_FILL)
    client.draw(d)
    facade = tab_box(d, 135, 520, 200, "wealth.dashboard",
                     ["WealthDashboard   «Facade»", "DashboardSummary"],
                     fill=FACADE_FILL)
    storage = tab_box(d, 0, 420, 112, "wealth.storage",
                      ["database.py «Singleton»", "repository.py"])
    pricing = tab_box(d, 119, 420, 112, "wealth.pricing",
                      ["providers.py", "sources.py «Factory Method»"])
    valuation = tab_box(d, 238, 420, 112, "wealth.valuation",
                        ["calculator.py", "fees.py «Decorator»"])
    reporting = tab_box(d, 357, 420, 113, "wealth.reporting",
                        ["exporters.py", "console.py"])
    assets = tab_box(d, 70, 320, 300, "wealth.assets",
                     ["component.py      «Composite: Component»",
                      "base.py           «Composite: Leaf»",
                      "group.py          «Composite: Composite»",
                      "factory.py        «Factory Method»",
                      "builder.py        «Builder + Director»",
                      "stock.py · crypto.py · cash.py · real_estate.py"])
    money_box = Box(385, 320, 85, "wealth.money", methods=["money()", "to_decimal()"],
                    fill=CLIENT_FILL, tag="used by every package")
    money_box.draw(d)

    connect(d, [(client.cx, client.bottom), (client.cx, facade.y)], "dep",
            label="«import»", label_at=(client.cx + 26, (client.bottom + facade.y) / 2 - 2))
    fan(d, facade, [storage, pricing, valuation, reporting], 446)
    fan_in(d, [storage, valuation], assets, 346)
    note(d, 0, 590, 145, ["Runtime imports point only", "downward or sideways:", "the package graph has", "no cycles."])
    return fit(d)


# ---------------------------------------------------------------------------
# 5.1  Singleton
# ---------------------------------------------------------------------------

def fig_singleton():
    d = Drawing(USABLE, 330)
    db = Box(190, 310, 200, "Database", stereo="singleton", fill=SINGLETON_FILL,
             attrs=["- _instance: Database  {static}", "- _lock: threading.Lock  {static}",
                    "- _path: str", "- _connection: sqlite3.Connection"],
             methods=["+ __new__(path=None): Database", "+ instance(): Database  {static}",
                      "+ connection: sqlite3.Connection", "- _reset()  {tests only}"])
    repo_a = Box(0, 300, 132, "repoA : AssetRepository",
                 methods=["+ save(portfolio)", "+ load()"])
    repo_b = Box(0, 238, 132, "repoB : AssetRepository",
                 methods=["+ save(portfolio)", "+ load()"])
    for b in (db, repo_a, repo_b):
        b.draw(d)
    connect(d, [(repo_a.right, repo_a.cy), (db.x, repo_a.cy)], "dep",
            label="same connection", label_at=(161, repo_a.cy + 5))
    connect(d, [(repo_b.right, repo_b.cy), (db.x, repo_b.cy)], "dep",
            label="same connection", label_at=(161, repo_b.cy + 5))
    connect(d, [(db.right, db.y - 24), (db.right + 28, db.y - 24),
                (db.right + 28, db.y - 62), (db.right, db.y - 62)], "assoc",
            label="_instance 0..1", label_at=(db.right + 52, db.y - 45))
    note(d, 120, db.bottom - 14, 290,
         ["__new__ takes the lock only while no instance exists (double-checked",
          "locking). Asking for a different file path raises an error instead of",
          "silently handing back the connection that is already open."])
    return fit(d)


# ---------------------------------------------------------------------------
# 5.2  Factory Method
# ---------------------------------------------------------------------------

def fig_factory():
    d = Drawing(USABLE, 330)
    creator = Box(0, 310, 205, "MarketDataSource", stereo="abstract · Creator",
                  abstract=True, fill=ABSTRACT_FILL,
                  attrs=["- _provider: PriceProvider"],
                  methods=["+ create_provider(): PriceProvider*",
                           "+ provider(): PriceProvider", "+ description: str*"])
    product = Box(265, 310, 205, "PriceProvider", stereo="interface · Product",
                  abstract=True, fill=IFACE_FILL,
                  methods=["+ get_price(symbol): Decimal*"])
    demo = Box(0, 200, 98, "DemoMarketData", stereo="ConcreteCreator",
               methods=["+ create_provider()"])
    live = Box(107, 200, 98, "LiveMarketData", stereo="ConcreteCreator",
               methods=["+ create_provider()"])
    api = Box(265, 200, 98, "ApiPriceProvider", stereo="ConcreteProduct",
              methods=["+ get_price()"])
    mock = Box(372, 200, 98, "MockPriceProvider", stereo="ConcreteProduct",
               methods=["+ get_price()"])
    for b in (creator, product, demo, live, api, mock):
        b.draw(d)
    tree(d, creator, [demo, live], 222)
    tree(d, product, [api, mock], 222, kind="realize")
    y_uses = 280
    connect(d, [(creator.right, y_uses), (product.x, y_uses)], "dep",
            label="«uses»", label_at=(235, y_uses + 4))
    connect(d, [(live.right, live.cy), (api.x, live.cy)], "dep",
            label="«creates»", label_at=(235, live.cy + 4))
    low = demo.bottom - 16
    connect(d, [(demo.cx, demo.bottom), (demo.cx, low), (mock.cx, low),
                (mock.cx, mock.bottom)], "dep",
            label="«creates»", label_at=(235, low - 9))
    note(d, 0, low - 22, 255,
         ["def provider(self):",
          "    if self._provider is None:",
          "        self._provider = CachingPriceProvider(self.create_provider())",
          "    return self._provider"])
    factory = Box(300, low - 22, 170, "AssetFactory",
                  stereo="parameterised factory method", fill=CREATION_FILL,
                  attrs=["- _registry: Dict[str, Type[Asset]]"],
                  methods=["+ register(cls)  {class decorator}",
                           "+ create(kind, symbol, qty, details): Asset"])
    factory.draw(d)
    return fit(d)


# ---------------------------------------------------------------------------
# 5.3  Builder
# ---------------------------------------------------------------------------

def fig_builder():
    d = Drawing(USABLE, 360)
    client = Box(0, 345, 140, "main.py", stereo="client",
                 methods=["director.demo_portfolio()"], fill=CLIENT_FILL)
    director = Box(0, 275, 150, "PortfolioDirector", stereo="Director",
                   attrs=["- _builder: PortfolioBuilder"],
                   methods=["+ demo_portfolio(): AssetGroup",
                            "+ starter_portfolio(): AssetGroup"])
    builder = Box(175, 345, 172, "PortfolioBuilder", stereo="Builder",
                  fill=CREATION_FILL,
                  attrs=["- _root: AssetGroup", "- _stack: List[AssetGroup]",
                         "- _symbols: Set[str]"],
                  methods=["+ group(name): self", "+ end(): self",
                           "+ stock(symbol, qty, exchange): self",
                           "+ crypto(symbol, qty, wallet): self",
                           "+ cash(label, balance, rate): self",
                           "+ real_estate(label, value, mortgage): self",
                           "+ build(): AssetGroup"])
    product = Box(375, 300, 95, "AssetGroup", stereo="Product",
                  methods=["the Composite tree"])
    for b in (client, director, builder, product):
        b.draw(d)
    connect(d, [(60, client.bottom), (60, director.y)], "dep")
    connect(d, [(director.right, director.cy), (builder.x, director.cy)], "aggregate")
    connect(d, [(builder.right, product.cy), (product.x, product.cy)], "dep",
            label="«builds»", label_at=(361, product.cy + 5))
    note(d, 0, director.bottom - 14, 160,
         ["The director owns the recipes;",
          "the builder owns the steps.",
          "One builder, many portfolios."])
    note(d, 175, builder.bottom - 14, 295,
         ["Every step returns self, so calls chain (fluent interface).",
          "build() rejects duplicates, negative quantities and unclosed",
          "groups, returns the tree and resets the builder for reuse."])
    return fit(d)


# ---------------------------------------------------------------------------
# 6.1  Composite
# ---------------------------------------------------------------------------

def fig_composite():
    d = Drawing(USABLE, 360)
    caption_text(d, 0, 352, "(a) class structure")
    comp = Box(35, 340, 180, "PortfolioComponent", stereo="abstract · Component",
               abstract=True, fill=ABSTRACT_FILL,
               methods=["+ name: str*", "+ market_value(prices)*", "+ walk(path)*",
                        "+ holdings()", "+ outline(depth)"])
    leaf = Box(0, 222, 105, "Asset", stereo="Leaf", abstract=True, fill=ABSTRACT_FILL,
               attrs=["+ symbol, quantity"], methods=["+ market_value()*"])
    group = Box(135, 222, 115, "AssetGroup", stereo="Composite",
                attrs=["- _children: List"],
                methods=["+ add(c) / remove(c)", "+ market_value() = Σ"])
    kids = [Box(i * 64, 128, 58, n) for i, n in
            enumerate(["Stock", "Crypto", "Cash", "RealEstate"])]
    for b in [comp, leaf, group] + kids:
        b.draw(d)
    tree(d, comp, [leaf, group], 240)
    tree(d, leaf, kids, 140)
    connect(d, [(group.right, group.cy), (260, group.cy), (260, comp.cy),
                (comp.right, comp.cy)], "aggregate",
            label="children 0..*", label_at=(238, comp.cy + 6))

    # (b) object tree computed from the real demo portfolio
    root, prices = demo_tree()
    x0, top, row = 284, 340, 17.5
    caption_text(d, x0, 352, "(b) the demo portfolio at run time")
    rows = []

    def visit(component, depth):
        rows.append((depth, component))
        for child in getattr(component, "children", ()):
            visit(child, depth + 1)
    visit(root, 0)
    anchors = {}
    for i, (depth, comp_) in enumerate(rows):
        y = top - i * row
        x = x0 + depth * 15
        w = USABLE - x
        is_group = isinstance(comp_, AssetGroup)
        d.add(Rect(x, y - 13, w, 13, fillColor=ABSTRACT_FILL if is_group else colors.white,
                   strokeColor=NAVY, strokeWidth=0.6))
        d.add(String(x + 4, y - 9.4, comp_.name, fontName=BODY_B if is_group else BODY,
                     fontSize=6.8, fillColor=NAVY if is_group else INK))
        d.add(String(USABLE - 4, y - 9.4, amount(comp_.market_value(prices)),
                     fontName=BODY_B if is_group else BODY, fontSize=6.8,
                     fillColor=INK, textAnchor="end"))
        anchors[i] = (x, y)
        if depth:
            parent = max(j for j in range(i) if rows[j][0] == depth - 1)
            px, py = anchors[parent]
            d.add(Line(px + 6, py - 13, px + 6, y - 6.5, strokeColor=NAVY, strokeWidth=0.6))
            d.add(Line(px + 6, y - 6.5, x, y - 6.5, strokeColor=NAVY, strokeWidth=0.6))
    return fit(d)


# ---------------------------------------------------------------------------
# 6.2  Decorator
# ---------------------------------------------------------------------------

def fig_decorator():
    d = Drawing(USABLE, 340)
    caption_text(d, 0, 332, "(a) class structure")
    comp = Box(50, 320, 170, "PortfolioComponent", stereo="abstract · Component",
               abstract=True, fill=ABSTRACT_FILL, methods=["+ market_value(prices)*"])
    asset = Box(0, 250, 100, "Asset", stereo="ConcreteComponent",
                methods=["+ market_value()"])
    deco = Box(118, 250, 152, "ValuationDecorator", stereo="Decorator",
               fill=CREATION_FILL,
               attrs=["- _inner: PortfolioComponent", "+ label: str"],
               methods=["+ market_value(): inner's value", "+ costs(): List[str]"])
    pct = Box(110, 140, 80, "PercentageFee", attrs=["+ rate"],
              methods=["v - v × rate"])
    fixed = Box(196, 140, 80, "FixedFee", attrs=["+ amount"],
                methods=["max(v - amount, 0)"])
    for b in (comp, asset, deco, pct, fixed):
        b.draw(d)
    tree(d, comp, [asset, deco], 266)
    tree(d, deco, [pct, fixed], 158)
    connect(d, [(deco.right, deco.cy), (284, deco.cy), (284, comp.cy),
                (comp.right, comp.cy)], "aggregate",
            label="inner 1", label_at=(258, comp.cy + 6))

    # (b) one real holding, wrapped twice, with the values the code produces
    _, prices = demo_tree()
    root = PortfolioDirector().demo_portfolio()
    btc = [a for a in root.holdings() if a.symbol == "BTC"][0]
    inner_pct = PercentageFee(btc, "0.01", "exchange fee 1%")
    outer = FixedFee(inner_pct, "15", "withdrawal fee EUR 15")
    reverse = PercentageFee(FixedFee(btc, "15"), "0.01")
    x0, top = 300, 320
    caption_text(d, x0, 332, "(b) BTC wrapped twice at run time")
    layers = [
        ("FixedFee", "withdrawal fee EUR 15", outer.market_value(prices), NEW_FILL),
        ("PercentageFee", "exchange fee 1%", inner_pct.market_value(prices), CREATION_FILL),
        ("Crypto  BTC × 0.35", "61,250.00 per coin", btc.market_value(prices), colors.white),
    ]
    width, height = USABLE - x0, 176
    for i, (name, sub, value, fill) in enumerate(layers):
        x, y, w, h = x0 + 13 * i, top - 29 * i, width - 26 * i, height - 45 * i
        d.add(Rect(x, y - h, w, h, rx=4, ry=4, fillColor=fill, strokeColor=NAVY,
                   strokeWidth=0.8))
        d.add(String(x + 6, y - 11, name, fontName=BODY_B, fontSize=7.4, fillColor=NAVY))
        d.add(String(x + 6, y - 20, sub, fontName=BODY_I, fontSize=6.6, fillColor=GREY))
        d.add(String(x + w - 6, y - h + 6, "= " + amount(value), fontName=BODY_B,
                     fontSize=7.4, fillColor=INK, textAnchor="end"))
    note(d, x0, top - height - 10, width,
         ["Order matters: wrapping the other way,",
          "PercentageFee(FixedFee(btc)), yields %s." % amount(reverse.market_value(prices))])
    return fit(d)


# ---------------------------------------------------------------------------
# 6.3  Facade
# ---------------------------------------------------------------------------

def fig_facade():
    d = Drawing(USABLE, 330)
    client = Box(165, 325, 140, "main.py / unit tests", stereo="client",
                 methods=["talks to the facade only"], fill=CLIENT_FILL)
    facade = Box(135, 268, 200, "WealthDashboard", stereo="Facade", fill=FACADE_FILL,
                 methods=["+ save_portfolio(portfolio): int", "+ summary(): DashboardSummary",
                          "+ report(): str", "+ export(path): str"])
    cols = [0, 120, 240, 360]
    row_a = [Box(cols[0], 158, 110, "AssetRepository", stereo="persistence"),
             Box(cols[1], 158, 110, "MarketDataSource", stereo="Factory Method"),
             Box(cols[2], 158, 110, "PortfolioCalculator", stereo="valuation"),
             Box(cols[3], 158, 110, "Exporters, renderer", stereo="reporting")]
    row_b = [Box(cols[0], 88, 110, "Database", stereo="Singleton", fill=SINGLETON_FILL),
             Box(cols[1], 88, 110, "PriceProvider", stereo="created product",
                 fill=IFACE_FILL),
             Box(cols[2], 88, 110, "LiquidationPolicy", stereo="wraps with Decorators",
                 fill=CREATION_FILL)]
    d.add(Rect(-6, 34, USABLE + 12, 140, fillColor=colors.HexColor("#FAFAFC"),
               strokeColor=colors.HexColor("#8A8FA3"), strokeWidth=0.7,
               strokeDashArray=(3, 3)))
    d.add(String(0, 40, "subsystem – the client never imports any of these classes",
                 fontName=BODY_I, fontSize=6.8, fillColor=GREY))
    for b in [client, facade] + row_a + row_b:
        b.draw(d)
    connect(d, [(client.cx, client.bottom), (client.cx, facade.y)], "dep")
    fan(d, facade, row_a, 172)
    for top_box, bottom_box in zip(row_a, row_b):
        connect(d, [(top_box.cx, top_box.bottom), (bottom_box.cx, bottom_box.y)], "dep")
    return fit(d)


# ---------------------------------------------------------------------------
# 6.4  Sequence of WealthDashboard.summary()
# ---------------------------------------------------------------------------

def fig_sequence():
    d = Drawing(USABLE, 330)
    labels = ["main.py", ":WealthDashboard", ":AssetRepository", ":PortfolioCalculator",
              ":LiquidationPolicy", "root :AssetGroup"]
    messages = [
        (0, 1, "1: summary()", "call"),
        (1, 2, "2: load()", "call"),
        (2, 1, "3: root (rebuilt tree)", "ret"),
        (1, 3, "4: value_positions(root, policy)", "call"),
        (3, 5, "5: walk()", "call"),
        (5, 3, "6: (path, asset) pairs", "ret"),
        (3, 4, "7: wrap(asset)", "call"),
        (4, 3, "8: FixedFee(PercentageFee(asset))", "ret"),
        (3, 1, "9: List[Position]", "ret"),
        (1, 3, "10: breakdown(root)", "call"),
        (3, 5, "11: outline() + market_value()", "call"),
        (1, 0, "12: DashboardSummary", "ret"),
    ]
    sequence(d, labels, messages, top=325, step=21,
             frames=[("loop [each holding]", 6, 7, 2, 4)])
    return fit(d)


FIGURES = [
    ("fig_packages", fig_packages), ("fig_singleton", fig_singleton),
    ("fig_factory", fig_factory), ("fig_builder", fig_builder),
    ("fig_composite", fig_composite), ("fig_decorator", fig_decorator),
    ("fig_facade", fig_facade), ("fig_sequence", fig_sequence),
]


def preview(outdir):
    """Writes each figure as a one-page PDF so it can be thumbnailed."""
    from reportlab.graphics import renderPDF
    for name, builder in FIGURES:
        renderPDF.drawToFile(builder(), os.path.join(outdir, name + ".pdf"))
        print(name)


if __name__ == "__main__":
    preview(sys.argv[1])
