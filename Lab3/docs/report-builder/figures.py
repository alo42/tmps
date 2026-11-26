"""PDF versions of the four Mermaid diagrams in REPORT.md (same classes, same relations)."""

from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib import colors

from styles import ABSTRACT_FILL, IFACE_FILL, NAVY, USABLE
from uml import Box, connect, fit, note, sequence, tree

CLIENT_FILL = colors.HexColor("#EDEDF3")
FLY_FILL = colors.HexColor("#EAF4EC")
PROXY_FILL = colors.HexColor("#E6F0FA")
CREATE_FILL = colors.HexColor("#FFF8E6")


def comb(d, parent, children, trunk_x, kind="inherit"):
    """Generalisation drawn as a comb: one arrow into the parent, a vertical
    trunk, and a horizontal stub into the left edge of each stacked child."""
    top = parent.bottom - 10
    connect(d, [(trunk_x, top), (trunk_x, parent.bottom)], kind)
    dash = (2.2, 2.2) if kind == "realize" else None
    d.add(Line(trunk_x, top, trunk_x, children[-1].cy, strokeColor=NAVY,
               strokeWidth=0.8, strokeDashArray=dash))
    for child in children:
        d.add(Line(trunk_x, child.cy, child.x, child.cy, strokeColor=NAVY,
                   strokeWidth=0.8, strokeDashArray=dash))


def fig_flyweight():
    d = Drawing(USABLE, 470)
    client = Box(135, 462, 200, "PortfolioBuilder", stereo="Client", fill=CLIENT_FILL,
                 methods=["+ Buy(symbol, quantity, unitCost, date)", "+ BuyMonthly(...)",
                          "+ Build(): IPortfolio"])
    lot = Box(0, 360, 190, "Lot", stereo="Context  (extrinsic state)",
              attrs=["+ Instrument: IInstrument", "+ Quantity: decimal", "+ UnitCost: decimal",
                     "+ Purchased: DateOnly"],
              methods=["+ CostBasis: decimal", "+ MarketValue(quotes): decimal"])
    factory = Box(255, 360, 215, "InstrumentFactory", stereo="FlyweightFactory", fill=CREATE_FILL,
                  attrs=["- _pool: ConcurrentDictionary<string, IInstrument>",
                         "- _create: Func<string, IInstrument>"],
                  methods=["+ Count: int", "+ Get(symbol): IInstrument"])
    iface = Box(0, 210, 190, "IInstrument", stereo="Flyweight interface", abstract=True,
                fill=IFACE_FILL,
                attrs=["+ Symbol, Name: string", "+ AssetClass: AssetClass",
                       "+ Exchange, Currency: string"],
                methods=["+ MarketValue(quantity, quotes): decimal*"])
    catalog = Box(255, 250, 215, "InstrumentCatalog", attrs=["+ Lookups: int"],
                  methods=["+ Create(symbol): IInstrument"])
    concrete = Box(0, 85, 190, "Instrument", stereo="ConcreteFlyweight", fill=FLY_FILL,
                   attrs=["+ Symbol, Name, AssetClass,", "  Exchange, Currency  {get only}"],
                   methods=["~ Instrument(...)  {internal}", "+ MarketValue(quantity, quotes)"])
    for b in (client, lot, factory, iface, catalog, concrete):
        b.draw(d)
    connect(d, [(client.cx + 60, client.bottom), (client.cx + 60, 378), (factory.cx, 378),
                (factory.cx, factory.y)], "dep", label="Get(symbol)", label_at=(factory.cx + 30, 382))
    connect(d, [(client.cx - 60, client.bottom), (client.cx - 60, 378), (lot.cx, 378),
                (lot.cx, lot.y)], "dep", label="creates", label_at=(lot.cx + 26, 382))
    connect(d, [(lot.cx, lot.bottom), (lot.cx, iface.y)], "assoc",
            label="shares  1", label_at=(lot.cx + 26, (lot.bottom + iface.y) / 2))
    connect(d, [(factory.x, factory.bottom + 14), (228, factory.bottom + 14), (228, iface.cy),
                (iface.right, iface.cy)], "aggregate",
            label="pools 0..*", label_at=(205, factory.bottom + 18))
    connect(d, [(factory.cx, factory.bottom), (factory.cx, catalog.y)], "dep",
            label="creates new ones via", label_at=(factory.cx + 52, (factory.bottom + catalog.y) / 2))
    connect(d, [(catalog.right - 12, catalog.bottom), (catalog.right - 12, concrete.cy),
                (concrete.right, concrete.cy)],
            "dep", label="constructs", label_at=(catalog.cx - 30, concrete.cy + 4))
    connect(d, [(concrete.cx, concrete.y), (concrete.cx, iface.bottom)], "realize")
    note(d, 255, 150, 185, ["Intrinsic, shared, immutable: Instrument.",
                            "Extrinsic, per purchase: Lot.",
                            "43 demo lots -> 6 Instrument objects."])
    return fit(d)


def fig_proxy():
    d = Drawing(USABLE, 470)
    client = Box(150, 462, 170, "Report", stereo="Client", fill=CLIENT_FILL,
                 methods=["+ Render(portfolio, quotes): string"])
    subject = Box(135, 395, 200, "IPortfolio", stereo="Subject interface", abstract=True,
                  fill=IFACE_FILL,
                  attrs=["+ Name: string", "+ Lots: IReadOnlyList<Lot>"],
                  methods=["+ AddLot(lot)*", "+ RemoveLot(lot): bool*"])
    real = Box(0, 260, 175, "Portfolio", stereo="RealSubject",
               attrs=["- _lots: List<Lot>", "+ Name, Lots"],
               methods=["+ AddLot(lot)", "+ RemoveLot(lot): bool"])
    proxy = Box(240, 260, 230, "PortfolioAccessProxy", stereo="Proxy", fill=PROXY_FILL,
                attrs=["- _real: IPortfolio", "- _user: User", "- _log: List<AccessEvent>"],
                methods=["+ Name, Lots   (check View)", "+ AddLot(lot)   (check Trade)",
                         "+ RemoveLot(lot)   (check Trade)", "+ AccessLog",
                         "- Demand(permission, action)"])
    exc = Box(0, 75, 150, "AccessDeniedException", attrs=["+ User", "+ Action"])
    user = Box(165, 75, 95, "User", attrs=["+ Name", "+ Role"])
    role = Box(275, 75, 105, "Role", attrs=["+ Name", "+ Permissions"],
               methods=["+ Allows(p): bool", "Owner, Advisor, Guest  {static}"])
    perm = Box(395, 75, 75, "Permission", stereo="enumeration", attrs=["None", "View", "Trade"])
    for b in (client, subject, real, proxy, exc, user, role, perm):
        b.draw(d)
    connect(d, [(client.cx, client.bottom), (client.cx, subject.y)], "dep",
            label="reads through", label_at=(client.cx + 40, (client.bottom + subject.y) / 2 - 2))
    tree(d, subject, [real, proxy], 290, kind="realize")
    connect(d, [(proxy.right - 12, proxy.y), (proxy.right - 12, subject.cy), (subject.right, subject.cy)],
            "assoc", label="_real: delegates to", label_at=(proxy.right - 62, subject.cy + 5))
    connect(d, [(proxy.x + 50, proxy.bottom), (proxy.x + 50, 104), (user.cx, 104), (user.cx, user.y)],
            "assoc", label="acts for", label_at=(proxy.x + 76, 108))
    connect(d, [(user.right, user.cy), (role.x, user.cy)], "assoc")
    connect(d, [(role.right, perm.cy), (perm.x, perm.cy)], "assoc")
    connect(d, [(proxy.x + 14, proxy.bottom), (proxy.x + 14, 124), (exc.cx, 124), (exc.cx, exc.y)],
            "dep", label="throws", label_at=(exc.cx + 22, 128))
    return fit(d)


def fig_bridge():
    d = Drawing(USABLE, 380)
    report = Box(0, 370, 215, "Report", stereo="Abstraction", abstract=True, fill=ABSTRACT_FILL,
                 attrs=["# Renderer: IReportRenderer", "# Heading: string*"],
                 methods=["+ Render(portfolio, quotes): string", "# Body(portfolio, quotes): string*"])
    impl = Box(255, 370, 215, "IReportRenderer", stereo="Implementor interface", abstract=True,
               fill=IFACE_FILL,
               methods=["+ Title(text): string*", "+ Table(columns, rows): string*",
                        "+ Field(label, value): string*"])
    reports = [Box(40, 270 - i * 48, 175, n, stereo="RefinedAbstraction", methods=["# Body(...)"])
               for i, n in enumerate(["HoldingsReport", "AllocationReport", "PerformanceReport"])]
    renderers = [Box(295, 270 - i * 48, 175, n, stereo="ConcreteImplementor",
                     methods=["+ Title, Table, Field"])
                 for i, n in enumerate(["ConsoleTableRenderer", "MarkdownRenderer", "CsvRenderer"])]
    factory = Box(0, 105, 200, "RendererFactory", stereo="Factory Method", fill=CREATE_FILL,
                  methods=["+ Register(format, creator)", "+ Create(format): IReportRenderer"])
    for b in [report, impl, factory] + reports + renderers:
        b.draw(d)
    y_bridge = report.y - 52
    connect(d, [(report.right, y_bridge), (impl.x, y_bridge)], "aggregate",
            label="bridge", label_at=(235, y_bridge + 6))
    comb(d, report, reports, 20)
    comb(d, impl, renderers, 275, kind="realize")
    connect(d, [(factory.right, factory.cy), (235, factory.cy), (235, impl.bottom - 6),
                (impl.x, impl.bottom - 6)], "dep",
            label="creates", label_at=(218, factory.cy + 5))
    note(d, 255, 112, 215, ["3 reports + 3 renderers = 6 classes,",
                               "9 combinations. A new format or report",
                               "is one new class on its own side."])
    return fit(d)


def fig_interaction():
    d = Drawing(USABLE, 330)
    labels = ["ConsoleDemo", "HoldingsReport", "MarkdownRenderer", "PortfolioAccessProxy",
              "Portfolio", "PortfolioValuation", "Instrument"]
    messages = [
        (0, 1, "1: Render(...)", "call"),
        (1, 3, "2: Name", "call"),
        (3, 3, "3: Demand(View) - allowed", "call"),
        (3, 4, "4: Name", "call"),
        (1, 2, "5: Title(...)", "call"),
        (1, 5, "6: Holdings(advisorProxy, quotes)", "call"),
        (5, 3, "7: Lots", "call"),
        (3, 3, "8: Demand(View) - allowed", "call"),
        (3, 4, "9: Lots", "call"),
        (5, 6, "10: MarketValue(...)", "call"),
        (1, 2, "11: Table(...)", "call"),
        (1, 2, "12: Field(...)", "call"),
        (1, 0, "13: text", "ret"),
    ]
    sequence(d, labels, messages, top=325, step=20,
             frames=[("loop [each instrument]", 9, 9, 5, 6)])
    return fit(d)


FIGURES = {
    "flyweight": fig_flyweight,
    "proxy": fig_proxy,
    "bridge": fig_bridge,
    "interaction": fig_interaction,
}
