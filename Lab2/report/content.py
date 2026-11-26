"""The text of the Lab 2 report. Code, output and figures come from the real project."""

import ast
import os
import subprocess
import sys
import textwrap

from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, Spacer

from styles import S, P, bullets, data_table, listing
import figures

LAB2 = figures.LAB2

from wealth import DemoMarketData, PortfolioDirector, WealthDashboard  # noqa: E402
from wealth.storage import Database  # noqa: E402


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def C(text):
    """Inline code."""
    return "<font name='Courier'>%s</font>" % text


def read(rel):
    with open(os.path.join(LAB2, rel), encoding="utf-8") as handle:
        return handle.read()


def code(rel, *names, drop_docstrings=False):
    """
    Source of one or more classes / functions / methods in a file, e.g.
    code("wealth/storage/database.py", "Database.__new__", "Database.instance").
    Decorators are kept; bodies are dedented to the left margin.
    """
    source = read(rel)
    lines = source.splitlines()
    tree = ast.parse(source)
    chunks = []
    for name in names:
        node = tree
        for part in name.split("."):
            node = next(n for n in ast.iter_child_nodes(node)
                        if isinstance(n, (ast.ClassDef, ast.FunctionDef))
                        and n.name == part)
        start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
        body = lines[start:node.end_lineno]
        if drop_docstrings and ast.get_docstring(node):
            doc = node.body[0]
            cut = set(range(doc.lineno - 1 - start, doc.end_lineno - start))
            body = [line for i, line in enumerate(body) if i not in cut]
        chunks.append(textwrap.dedent("\n".join(body)))
    return "\n\n".join(chunks)


def run(*args):
    result = subprocess.run([sys.executable] + list(args), cwd=LAB2,
                            capture_output=True, text=True)
    return result.stdout + result.stderr


def figure(drawing, number, caption):
    return KeepTogether([drawing, P("Figure %s – %s" % (number, caption), "caption")])


def code_block(text, number, caption, fs="code"):
    block = [listing(text, fs=fs), P("Listing %s – %s" % (number, caption), "caption")]
    # long listings may split across pages; short ones stay with their caption
    return [KeepTogether(block)] if text.count("\n") < 45 else block


def table(rows, widths, number, caption):
    return [KeepTogether([data_table(rows, widths),
                          P("Table %s – %s" % (number, caption), "caption")])]


def demo_summary():
    Database._reset()
    dashboard = WealthDashboard(DemoMarketData())
    dashboard.save_portfolio(PortfolioDirector().demo_portfolio())
    return dashboard.summary()


def amount(value):
    return "{:,}".format(value)


# ---------------------------------------------------------------------------
# 1-3
# ---------------------------------------------------------------------------

def purpose():
    st = [P("1   Purpose of the Work", "h1")]
    st += [P(
        "The purpose of this laboratory work is to study creational and structural "
        "design patterns and to apply them to the system developed in Laboratory Work "
        "No. 1: a <b>Personal Wealth Dashboard and Multi-Asset Portfolio Tracker</b> that "
        "computes a user's net worth across stocks, cryptocurrencies, savings and real "
        "estate. The objectives were:")]
    st += bullets([
        "to study the intent, structure and consequences of the creational and structural "
        "patterns described by Gamma et al. [1];",
        "to identify, in the existing system, the instantiation problems that creational "
        "patterns solve and the composition problems that structural patterns solve;",
        "to implement three creational patterns – <b>Singleton</b>, <b>Factory "
        "Method</b> and <b>Builder</b> – and three structural patterns – "
        "<b>Composite</b>, <b>Decorator</b> and <b>Facade</b>;",
        "to restructure the single-file implementation of Lab 1 into a package with one "
        "module per responsibility;",
        "to verify every pattern with automated tests and to document the design in UML.",
    ])
    st += [P(
        "The work is a separate project (folder %s); the Lab 1 sources were left untouched. "
        "It requires Python 3.9 or later and uses the standard library only." % C("Lab2/"))]
    return st


def theory():
    st = [P("2   Theoretical Background", "h1")]
    st += [P("2.1   Creational patterns", "h2")]
    st += [P(
        "Creational patterns abstract the instantiation process. They make a system "
        "independent of how its objects are created, composed and represented, so that "
        "<i>which</i> object is created, <i>when</i> and <i>how</i> can change without "
        "touching the code that uses it [1].")]
    st += bullets([
        "<b>Singleton</b> ensures a class has only one instance and provides a global "
        "point of access to it. It is the most criticised pattern of the catalogue because "
        "a global instance is hidden shared state; in practice it must be made thread-safe "
        "and it must remain replaceable in tests [3].",
        "<b>Factory Method</b> defines an interface for creating an object but lets "
        "subclasses decide which class to instantiate. The <i>creator</i> declares the "
        "factory method and usually contains logic that depends on it; "
        "<i>concrete creators</i> override it to return a <i>concrete product</i>. A "
        "common variant is the <i>parameterised</i> factory method, which receives an "
        "identifier of the kind of object to create [1].",
        "<b>Builder</b> separates the construction of a complex object from its "
        "representation, so the same construction process can produce different "
        "results. The <i>builder</i> exposes the construction steps, the <i>director</i> "
        "knows the order of steps for a given result, and the <i>product</i> is returned "
        "only when complete [1, 2].",
    ])
    st += [P("2.2   Structural patterns", "h2")]
    st += [P(
        "Structural patterns are concerned with how classes and objects are composed to "
        "form larger structures while keeping those structures flexible and efficient [1].")]
    st += bullets([
        "<b>Composite</b> composes objects into tree structures to represent part–whole "
        "hierarchies, and lets clients treat individual objects and compositions of "
        "objects uniformly through a common <i>component</i> interface.",
        "<b>Decorator</b> attaches additional responsibilities to an object dynamically. A "
        "decorator implements the same interface as the object it wraps and forwards to "
        "it, adding behaviour before or after; decorators can be stacked, which makes the "
        "pattern a flexible alternative to subclassing for every combination of features.",
        "<b>Facade</b> provides a unified, higher-level interface to a set of interfaces in "
        "a subsystem, making the subsystem easier to use without preventing direct access "
        "to it when a client really needs it.",
    ])
    st += table([
        ["Pattern", "Category", "Intent in one line", "Applied to"],
        ["Singleton", "Creational", "exactly one instance, globally reachable",
         C("Database")],
        ["Factory Method", "Creational", "subclasses choose the class to instantiate",
         C("MarketDataSource") + ", " + C("AssetFactory")],
        ["Builder", "Creational", "step-by-step construction of a complex product",
         C("PortfolioBuilder") + ", " + C("PortfolioDirector")],
        ["Composite", "Structural", "trees where leaves and groups look the same",
         C("PortfolioComponent") + ", " + C("AssetGroup")],
        ["Decorator", "Structural", "stackable wrappers that add behaviour",
         C("PercentageFee") + ", " + C("FixedFee")],
        ["Facade", "Structural", "one simple entry point to a subsystem",
         C("WealthDashboard")],
    ], [2.6 * cm, 2.2 * cm, 5.4 * cm, 5.6 * cm], "2.1",
        "The six patterns implemented in this work")
    return st


def requirements():
    st = [P("3   From Lab 1 to Lab 2: New Requirements", "h1")]
    st += [P(
        "Laboratory Work No. 1 produced a flat list of holdings valued at market price. "
        "Using it as a real dashboard exposed six shortcomings. Each one is a recurring "
        "design problem that a catalogue pattern addresses, so the patterns in this work "
        "were chosen <i>from</i> the requirements rather than added for their own sake "
        "(Table 3.1).")]
    st += table([
        ["#", "Requirement", "Why Lab 1 could not meet it", "Pattern"],
        ["R1", "Organise holdings into accounts and sub-accounts, with a subtotal for each",
         "holdings were a flat list", "Composite"],
        ["R2", "Create portfolios readably and reject invalid ones before they are stored",
         "objects were built with raw constructors, no validation", "Builder"],
        ["R3", "Every part of the application must share one database",
         "each repository opened its own connection", "Singleton"],
        ["R4", "Switch between demo and live prices without the client naming provider classes",
         "the entry point instantiated the mock provider itself", "Factory Method"],
        ["R5", "Show what the portfolio would return if sold, net of fees",
         "only the market value existed; fees would need a subclass per combination",
         "Decorator"],
        ["R6", "Give a user interface one small entry point",
         "a client had to wire seven collaborating classes", "Facade"],
    ], [0.9 * cm, 6.0 * cm, 5.6 * cm, 3.0 * cm], "3.1",
        "Requirements traced to the patterns that satisfy them")
    return st


# ---------------------------------------------------------------------------
# 4
# ---------------------------------------------------------------------------

TREE = """
Lab2/
|-- main.py                     client: uses only the facade and the director
|-- wealth/
|   |-- __init__.py             public API: WealthDashboard, PortfolioDirector, ...
|   |-- money.py                Decimal helpers: money(), to_decimal()
|   |-- dashboard.py            FACADE           WealthDashboard, DashboardSummary
|   |-- assets/
|   |   |-- component.py        COMPOSITE        PortfolioComponent (component)
|   |   |-- base.py             COMPOSITE        Asset (leaf)
|   |   |-- group.py            COMPOSITE        AssetGroup (composite)
|   |   |-- factory.py          FACTORY METHOD   AssetFactory (parameterised)
|   |   |-- builder.py          BUILDER          PortfolioBuilder, PortfolioDirector
|   |   |-- stock.py  crypto.py  cash.py  real_estate.py      one asset type each
|   |-- pricing/
|   |   |-- providers.py        PriceProvider, Mock / Api / CachingPriceProvider
|   |   |-- sources.py          FACTORY METHOD   MarketDataSource + 2 creators
|   |-- storage/
|   |   |-- database.py         SINGLETON        Database
|   |   |-- repository.py       AssetRepository
|   |-- valuation/
|   |   |-- calculator.py       PortfolioCalculator, Position
|   |   |-- fees.py             DECORATOR        PercentageFee, FixedFee, policy
|   |-- reporting/
|       |-- exporters.py        CsvExporter, JsonExporter
|       |-- console.py          render_summary()
|-- tests/test_patterns.py      25 unit tests, one test class per pattern
|-- report/                     this report's generator (styles, uml, figures, ...)
"""


def structure():
    st = [P("4   Project Structure", "h1")]
    st += [P("4.1   From one file to a package", "h2")]
    st += [P(
        "Lab 1 kept fifteen classes in a single 449-line module, %s. That was "
        "convenient for a first demonstration but it does not scale: every change "
        "reopened the same file, and the boundaries between responsibilities existed only "
        "as comments. In Lab 2 the module was split into the package %s, where each "
        "responsibility from Lab 1 became a sub-package and, as far as practical, each "
        "class family became a module (Listing 4.1). Every pattern therefore lives in a "
        "file that can be named in one sentence." % (C("wealth_dashboard.py"), C("wealth")))]
    st += code_block(TREE, "4.1", "Layout of the Lab 2 project")
    st += [P("The split follows three rules:")]
    st += bullets([
        "<b>one sub-package per responsibility</b> – storage, pricing, valuation, "
        "reporting and the asset model – so the Single-Responsibility Principle of "
        "Lab 1 now holds at package level as well as at class level;",
        "<b>imports point downward</b>: the facade depends on the sub-packages and the "
        "sub-packages depend on the asset model, never the reverse. Where a module needs "
        "another one only for a type annotation, the import is placed under "
        "%s, which keeps the run-time dependency graph free of cycles (Figure 4.1);"
        % C("typing.TYPE_CHECKING"),
        "<b>a small public surface</b>: each %s re-exports the names clients are meant "
        "to use, so %s imports just three names from %s." % (
            C("__init__.py"), C("main.py"), C("wealth")),
    ])
    st += [figure(figures.fig_packages(), "4.1",
                  "Package diagram: sub-packages, the pattern each one hosts, and their imports")]
    st += table([
        ["Lab 1 (single file)", "Lab 2 module"],
        [C("Asset") + ", " + C("Stock") + ", " + C("Crypto") + ", " + C("CashSavings")
         + ", " + C("RealEstate"), C("wealth/assets/base.py") + " + one module per type"],
        [C("ASSET_REGISTRY") + ", " + C("register_asset"), C("wealth/assets/factory.py")
         + " (now " + C("AssetFactory") + ")"],
        [C("PriceProvider") + " and its three implementations", C("wealth/pricing/providers.py")],
        [C("demo_prices()") + " in the entry point", C("wealth/pricing/sources.py")
         + " (now a factory method)"],
        [C("AssetRepository") + " with its own " + C("sqlite3.connect"),
         C("wealth/storage/repository.py") + " + " + C("database.py")],
        [C("PortfolioCalculator") + ", " + C("Position"), C("wealth/valuation/calculator.py")],
        [C("CsvExporter") + ", " + C("JsonExporter"), C("wealth/reporting/exporters.py")],
        [C("main()") + " with printing and wiring", C("main.py") + ", "
         + C("wealth/dashboard.py") + ", " + C("wealth/reporting/console.py")],
    ], [7.6 * cm, 8.2 * cm], "4.1", "Where each element of Lab 1 lives now")
    st += [KeepTogether([P("The project is run and tested from the %s folder:" % C("Lab2"))]
                        + code_block("python3 main.py           # dashboard + output/portfolio.csv|json\n"
                     "python3 -m unittest -v   # 25 tests, one test class per pattern",
                     "4.2", "Commands"))]
    return st


# ---------------------------------------------------------------------------
# 5  creational
# ---------------------------------------------------------------------------

def creational():
    st = [P("5   Creational Design Patterns", "h1")]

    # --- Singleton ----------------------------------------------------------
    st += [P("5.1   Singleton – Database", "h2")]
    st += [P(
        "<b>Problem.</b> In Lab 1 every %s opened its own SQLite connection. With the "
        "in-memory database used for the demonstration this is not merely wasteful but "
        "wrong: SQLite gives each connection to %s its own, separate, empty database [7], "
        "so a second repository could never see the portfolio saved by the first. "
        "Requirement R3 asks for exactly one connection per process." % (
            C("AssetRepository"), C(":memory:")))]
    st += [P(
        "<b>Solution.</b> %s controls its own instantiation in %s: the first call creates "
        "the connection, every later call returns the same object (Figure 5.1). Creation "
        "uses <i>double-checked locking</i> – the lock is taken only while no instance "
        "exists, and the condition is re-checked inside the lock so two threads cannot "
        "both create one. A request for a <i>different</i> database file raises an error "
        "instead of quietly returning the connection that is already open, which would hide "
        "a configuration bug." % (C("Database"), C("__new__")))]
    st += [figure(figures.fig_singleton(), "5.1", "Singleton: two repositories, one Database")]
    st += code_block(code("wealth/storage/database.py", "Database.__new__",
                          "Database.instance", "Database._reset"),
                     "5.1", "Database.__new__, instance() and the test hook")
    st += [P(
        "<b>Consequences.</b> The classic objection to Singleton is hidden global state. "
        "Two decisions limit it here. First, %s does not reach for the singleton "
        "internally: it receives a %s through its constructor and only falls back to "
        "%s when none is given, so the Dependency Inversion of Lab 1 still holds. Second, "
        "%s lets each unit test start from a fresh connection. The tests check identity, "
        "shared data between two repositories, refusal of a second path, and that sixteen "
        "threads racing on first use still produce a single instance." % (
            C("AssetRepository"), C("Database"), C("Database.instance()"),
            C("Database._reset()")))]

    # --- Factory Method -----------------------------------------------------
    st += [P("5.2   Factory Method – MarketDataSource and AssetFactory", "h2")]
    st += [P(
        "<b>Problem.</b> In Lab 1 the entry point constructed %s itself and remembered to "
        "wrap it in %s. Switching to live prices meant editing that code – and "
        "forgetting the cache would silently multiply API calls (R4)." % (
            C("MockPriceProvider"), C("CachingPriceProvider")))]
    st += [P(
        "<b>Solution.</b> %s is the <i>creator</i>. Its factory method %s is abstract; "
        "%s and %s are the <i>concrete creators</i> that return a %s or an %s "
        "respectively. The creator's own operation, %s, calls the factory method once and "
        "always wraps the result in the cache, so every source – including ones "
        "written in the future – gets caching for free (Figure 5.2)." % (
            C("MarketDataSource"), C("create_provider()"), C("DemoMarketData"),
            C("LiveMarketData"), C("MockPriceProvider"), C("ApiPriceProvider"),
            C("provider()")))]
    st += [figure(figures.fig_factory(), "5.2",
                  "Factory Method: parallel creator and product hierarchies, plus the "
                  "parameterised AssetFactory")]
    st += code_block(code("wealth/pricing/sources.py", "MarketDataSource",
                          "DemoMarketData", drop_docstrings=True),
                     "5.2", "The creator and one concrete creator")
    st += [P(
        "The second application is the <i>parameterised</i> variant. When the repository "
        "reads a row it only knows a type tag such as %s. %s maps the tag to the class "
        "that registered it with a class decorator, so neither the factory nor the "
        "repository names a single concrete asset type, and a new asset type needs no "
        "edit outside its own module:" % (C("'crypto'"), C("AssetFactory.create()")))]
    st += code_block(code("wealth/assets/factory.py", "AssetFactory.register",
                          "AssetFactory.create") + "\n\n\n"
                     + code("wealth/assets/stock.py", "Stock"),
                     "5.3", "Parameterised factory method and a self-registering product")
    st += [P(
        "<b>Consequences.</b> Clients depend only on %s; adding a data source is one new "
        "subclass. The price paid is a parallel hierarchy – one creator per product "
        "– which is acceptable for two or three sources." % C("MarketDataSource"))]

    # --- Builder ------------------------------------------------------------
    st += [P("5.3   Builder – PortfolioBuilder and PortfolioDirector", "h2")]
    st += [P(
        "<b>Problem.</b> With accounts (R1) a portfolio becomes a tree. Building it with "
        "constructors means creating every group, appending children in the right order, "
        "converting every amount to %s and checking for duplicate holdings – and a "
        "half-built tree could be saved by mistake (R2)." % C("Decimal"))]
    st += [P(
        "<b>Solution.</b> %s exposes one method per construction step. %s and %s open and "
        "close a nested group using a stack, so the shape of the call chain mirrors the "
        "shape of the tree. Every step returns %s, giving a fluent interface. %s refuses "
        "unclosed groups, duplicates, negative quantities, mortgages larger than the "
        "property and empty portfolios; it returns the finished tree and resets the builder "
        "so that one builder can serve many recipes. %s is the <i>director</i>: it owns the "
        "recipes and delegates every step (Figure 5.3)." % (
            C("PortfolioBuilder"), C("group()"), C("end()"), C("self"), C("build()"),
            C("PortfolioDirector")))]
    st += [figure(figures.fig_builder(), "5.3", "Builder: director, builder and product")]
    st += code_block(code("wealth/assets/builder.py", "PortfolioDirector.demo_portfolio",
                          drop_docstrings=True),
                     "5.4", "A director recipe – the indentation mirrors the resulting tree")
    st += code_block(code("wealth/assets/builder.py", "PortfolioBuilder.group",
                          "PortfolioBuilder.end", "PortfolioBuilder.build",
                          "PortfolioBuilder._add", drop_docstrings=True),
                     "5.5", "Structure steps and validation inside the builder")
    st += [P(
        "Amounts are accepted as strings, integers, %s or even floats; %s converts a float "
        "through %s, so %s becomes exactly 0.35 rather than the binary approximation "
        "0.34999999999999997779… – a test checks this. <b>Consequences.</b> The "
        "client code is short and readable, and an invalid portfolio cannot reach the "
        "database. For a single holding the builder is more ceremony than a constructor, "
        "which is why the asset classes remain directly constructible." % (
            C("Decimal"), C("to_decimal()"), C("str()"), C("0.35")))]
    return st


# ---------------------------------------------------------------------------
# 6  structural
# ---------------------------------------------------------------------------

def structural():
    st = [P("6   Structural Design Patterns", "h1")]

    # --- Composite ----------------------------------------------------------
    st += [P("6.1   Composite – PortfolioComponent, Asset and AssetGroup", "h2")]
    st += [P(
        "<b>Problem.</b> Requirement R1 asks for accounts inside accounts, each with a "
        "subtotal, while the calculator, the repository and the exporters of Lab 1 all "
        "expected a flat list of assets.")]
    st += [P(
        "<b>Solution.</b> %s is the <i>component</i> interface: %s, %s, %s (every leaf "
        "with the names of the groups above it) and %s (every group with its depth). %s is "
        "the <i>leaf</i>; %s is the <i>composite</i>, whose value is the sum of its "
        "children and whose %s and %s simply recurse (Figure 6.1, Listing 6.1)." % (
            C("PortfolioComponent"), C("name"), C("market_value()"), C("walk()"),
            C("outline()"), C("Asset"), C("AssetGroup"), C("walk()"), C("outline()")))]
    st += [figure(figures.fig_composite(), "6.1",
                  "Composite: (a) the class structure, (b) the demo portfolio as a live tree")]
    st += code_block(code("wealth/assets/group.py", "AssetGroup.market_value",
                          "AssetGroup.walk", "AssetGroup.outline")
                     + "\n\n\n# the leaf's half of the same contract (wealth/assets/base.py)\n"
                     + code("wealth/assets/base.py", "Asset.walk"),
                     "6.1", "The uniform interface, implemented by composite and leaf")
    st += [P(
        "The benefit is that every consumer now receives a %s and does not care what it "
        "is. The calculator values a single %s, the Stocks account or the whole net worth "
        "with the same call – a test asserts exactly that – and the per-account "
        "subtotals on the dashboard are just %s on each group. The repository stores the "
        "group path of each holding (for example %s) and rebuilds the tree on load. The "
        "implementation is the <i>safe</i> variant of the pattern: %s and %s exist only "
        "on %s, so a leaf can never be asked to accept children [1]." % (
            C("PortfolioComponent"), C("Stock"), C("market_value()"),
            C("Investments/Crypto"), C("add()"), C("remove()"), C("AssetGroup")))]

    # --- Decorator ----------------------------------------------------------
    st += [P("6.2   Decorator – ValuationDecorator, PercentageFee and FixedFee", "h2")]
    st += [P(
        "<b>Problem.</b> Market value overstates what a user would actually receive. "
        "Selling incurs brokerage commission on stocks, an exchange fee plus a network "
        "withdrawal fee on crypto, and an estate agent plus a notary on property (R5). "
        "Modelling this with subclasses would need one class per asset type per "
        "combination of fees, and every change of fees would edit the asset model.")]
    st += [P(
        "<b>Solution.</b> %s implements %s and holds another one; by default it forwards "
        "every call. %s and %s override only %s (Figure 6.2, Listing 6.2). Which wrappers "
        "apply to which kind of asset is data, held by %s (Listing 6.3); the calculator "
        "asks the policy to wrap each holding and reports both the market value and the "
        "value if sold. No asset class was modified." % (
            C("ValuationDecorator"), C("PortfolioComponent"), C("PercentageFee"),
            C("FixedFee"), C("market_value()"), C("LiquidationPolicy")))]
    st += [figure(figures.fig_decorator(), "6.2",
                  "Decorator: (a) the class structure, (b) one holding wrapped twice")]
    st += code_block(code("wealth/valuation/fees.py", "ValuationDecorator.__init__",
                          "ValuationDecorator.market_value", "PercentageFee",
                          "FixedFee", drop_docstrings=True),
                     "6.2", "The decorator base and the two concrete decorators")
    st += code_block(code("wealth/valuation/fees.py", "LiquidationPolicy.wrap",
                          "LiquidationPolicy.default", drop_docstrings=True),
                     "6.3", "The policy: configuration that decides the wrapping")
    st += [P(
        "Two properties of the pattern showed up concretely. First, <b>the order of "
        "wrapping is the order of application</b>: a 1%% fee followed by a EUR 15 fee "
        "leaves 21,208.13 of the BTC holding, while the reverse order leaves 21,208.28. "
        "The policy chooses the order in which an exchange actually charges, and a test "
        "pins both results. Second, because a decorator is itself a %s, it can wrap a "
        "<i>group</i> as easily as a holding – Composite and Decorator compose. "
        "The project also contains a decorator on the price side: %s from Lab 1 wraps any "
        "%s to add caching." % (C("PortfolioComponent"), C("CachingPriceProvider"),
                                C("PriceProvider")))]
    st += [P(
        "One modelling detail: a percentage of a property's <i>equity</i> would "
        "understate the agent's fee, which is charged on the sale price. The default policy "
        "therefore expresses property costs as fixed amounts derived from the appraisal.")]

    # --- Facade -------------------------------------------------------------
    st += [P("6.3   Facade – WealthDashboard", "h2")]
    st += [P(
        "<b>Problem.</b> After the five patterns above, producing a dashboard involves a "
        "database, a repository, a market data source, a calculator, a liquidation "
        "policy, two exporters and a renderer. Every user interface would have to wire "
        "them in the right order (R6).")]
    st += [P(
        "<b>Solution.</b> %s offers four methods – %s, %s, %s and %s – and "
        "wires the subsystem in its constructor (Figure 6.3). The export format is chosen "
        "from the file extension. As a result the entire client is the short %s in "
        "Listing 6.4." % (C("WealthDashboard"), C("save_portfolio()"), C("summary()"),
                          C("report()"), C("export()"), C("main()")))]
    st += [figure(figures.fig_facade(), "6.3", "Facade: one entry point in front of the subsystem")]
    st += code_block(code("main.py", "main"), "6.4", "The whole client, written against the facade")
    st += code_block(code("wealth/dashboard.py", "WealthDashboard.__init__",
                          "WealthDashboard.summary", "WealthDashboard.export",
                          drop_docstrings=True),
                     "6.5", "The facade's wiring and its two main operations")
    st += [P(
        "A facade simplifies; it does not imprison. The unit tests still use %s, %s and "
        "%s directly, which is exactly the flexibility the pattern is meant to preserve. "
        "Kept to four methods, the facade also avoids its usual failure mode of growing "
        "into a class that knows everything." % (
            C("AssetRepository"), C("PercentageFee"), C("DemoMarketData")))]

    st += [P("6.4   How the patterns cooperate", "h2")]
    st += [P(
        "Figure 6.4 follows one call to %s. The facade asks the repository for the "
        "portfolio; the repository uses the singleton connection, and %s rebuilds each "
        "holding into a Composite tree. The calculator walks the tree and asks the policy "
        "to decorate each holding. Every price lookup goes through the provider created by "
        "the factory method and wrapped in the caching decorator, so although each of the "
        "four priced holdings is valued at least four times (gross, net, its group, the "
        "root), the mock provider is called exactly four times – one of the tests "
        "asserts this number." % (C("summary()"), C("AssetFactory")))]
    st += [figure(figures.fig_sequence(), "6.4", "Sequence diagram of WealthDashboard.summary()")]
    return st


# ---------------------------------------------------------------------------
# 7-10
# ---------------------------------------------------------------------------

def results():
    output = run("main.py")
    tests = run("-m", "unittest", "-v")
    summary = demo_summary()
    csv_text = read("output/portfolio.csv")

    st = [P("7   Results", "h1")]
    st += [P(
        "The program was executed with CPython %d.%d on macOS with no third-party packages. "
        "The demo portfolio is the Lab 1 portfolio, now built by the director and "
        "organised into three accounts; its market value, %s, is unchanged from Lab 1, "
        "which confirms that the restructuring did not alter any valuation." % (
            sys.version_info[0], sys.version_info[1], amount(summary.net_worth)))]
    st += code_block("$ python3 main.py\n" + output.rstrip(), "7.1", "Program output",
                     fs="code_sm")

    rows = [["Holding", "Account", "Market value", "If sold", "Selling cost"]]
    for p in summary.positions:
        rows.append([p.symbol, p.group, amount(p.value), amount(p.net_value),
                     amount(p.selling_cost) if p.selling_cost else "–"])
    rows.append(["<b>Total</b>", "", "<b>%s</b>" % amount(summary.net_worth),
                 "<b>%s</b>" % amount(summary.liquidation_value),
                 "<b>%s</b>" % amount(summary.selling_cost)])
    st += [P(
        "Table 7.1 isolates the effect of the decorators. Selling everything today would "
        "cost %s, or %.1f%% of net worth; most of it is property costs." % (
            amount(summary.selling_cost),
            float(summary.selling_cost / summary.net_worth * 100)))]
    st += table(rows, [3.3 * cm, 3.6 * cm, 2.8 * cm, 2.7 * cm, 2.7 * cm], "7.1",
                "Market value and liquidation value per holding")
    st += [P("The exporters, selected by the facade from the file extension, wrote:")]
    st += code_block(csv_text.strip(), "7.2", "output/portfolio.csv")
    passed = tests.count(" ... ok")
    st += [P(
        "Finally, the test suite (Listing 7.3) exercises every pattern through its "
        "observable behaviour rather than its implementation details: %d tests, all "
        "passing." % passed)]
    st += code_block("$ python3 -m unittest -v\n" + tests.strip(), "7.3",
                     "Unit test run", fs="code_sm")
    return st


def discussion():
    st = [P("8   Discussion", "h1")]
    st += bullets([
        "<b>Patterns and the SOLID principles of Lab 1 reinforce each other.</b> Adding "
        "an asset type is still one new module (Open/Closed), now also picked up by the "
        "factory and the builder; a new kind of fee is one new decorator class; a new data "
        "source is one new creator subclass. The calculator still depends only on "
        "abstractions (Dependency Inversion).",
        "<b>One extension point is not fully closed.</b> A new export format is one new "
        "exporter class plus one entry in the facade's extension table. A registry like "
        "the one used for assets would remove that edit, at the cost of more indirection "
        "than two formats justify.",
        "<b>Singleton remains a trade-off.</b> It solves a real problem here (separate "
        "in-memory databases), but it is global state; constructor injection and the test "
        "hook keep it manageable rather than invisible.",
        "<b>Decorator order is semantics.</b> Stacking is powerful precisely because order "
        "matters, which also makes it a source of subtle errors. Keeping the order in one "
        "place, the policy, and pinning it with a test is the mitigation used here.",
        "<b>Rounding.</b> As in Lab 1, the allocation percentages are rounded independently "
        "and sum to 100.01%; totals are always computed from rounded positions so that the "
        "table and its total agree.",
    ])
    return st


def conclusions():
    st = [P("9   Conclusions", "h1")]
    st += [P(
        "Six design patterns were implemented in the portfolio tracker, each in response "
        "to a concrete requirement that the Lab 1 design could not meet. The creational "
        "patterns now control how objects come into existence: a <b>Singleton</b> "
        "guarantees one shared database connection, which turned out to be a correctness "
        "requirement for SQLite's in-memory mode; a <b>Factory Method</b> lets the choice "
        "of price source vary while guaranteeing caching for every source, and its "
        "parameterised form lets the repository recreate assets without naming their "
        "classes; a <b>Builder</b> with a director turns the construction of a nested, "
        "validated portfolio into a readable chain of calls. The structural patterns "
        "shape how objects are combined: <b>Composite</b> makes a single holding and an "
        "entire net worth interchangeable, <b>Decorator</b> layers selling costs onto any "
        "component without touching the asset model, and a <b>Facade</b> reduces the "
        "client to a handful of statements.")]
    st += [P(
        "The single Lab 1 file was reorganised into a package of %s modules with "
        "downward-only imports, and 25 automated tests verify each pattern by its "
        "behaviour. The main lesson is that the patterns paid off where they interacted: "
        "decorators wrap composites, the builder produces the composite, the factory "
        "method installs a decorator, and the facade hides all of it – so the "
        "dashboard gained account subtotals, a liquidation view and swappable price "
        "sources while its client became shorter than in Lab 1." % count_modules())]
    return st


def references():
    st = [P("10   References", "h1")]
    refs = [
        "Gamma, E., Helm, R., Johnson, R., Vlissides, J. <i>Design Patterns: Elements of "
        "Reusable Object-Oriented Software.</i> Addison-Wesley, 1994.",
        "Freeman, E., Robson, E. <i>Head First Design Patterns</i>, 2nd ed. O'Reilly, 2020.",
        "Shvets, A. <i>Dive Into Design Patterns.</i> Refactoring.Guru, 2019. "
        "https://refactoring.guru/design-patterns",
        "Martin, R. C. <i>Clean Architecture: A Craftsman's Guide to Software Structure "
        "and Design.</i> Prentice Hall, 2017.",
        "Python Software Foundation. <i>The Python Standard Library</i> – "
        "abc, dataclasses, decimal, sqlite3, threading, unittest. "
        "https://docs.python.org/3/library/",
        "Python Software Foundation. <i>typing.TYPE_CHECKING.</i> "
        "https://docs.python.org/3/library/typing.html",
        "SQLite Consortium. <i>In-Memory Databases.</i> https://www.sqlite.org/inmemorydb.html",
    ]
    st += [Paragraph("[%d]&nbsp;&nbsp;%s" % (i + 1, t), S["ref"]) for i, t in enumerate(refs)]
    return st


# ---------------------------------------------------------------------------
# Appendix
# ---------------------------------------------------------------------------

APPENDIX_ORDER = [
    "main.py", "wealth/money.py", "wealth/dashboard.py",
    "wealth/assets/component.py", "wealth/assets/base.py", "wealth/assets/group.py",
    "wealth/assets/factory.py", "wealth/assets/builder.py", "wealth/assets/stock.py",
    "wealth/assets/crypto.py", "wealth/assets/cash.py", "wealth/assets/real_estate.py",
    "wealth/pricing/providers.py", "wealth/pricing/sources.py",
    "wealth/storage/database.py", "wealth/storage/repository.py",
    "wealth/valuation/fees.py", "wealth/valuation/calculator.py",
    "wealth/reporting/exporters.py", "wealth/reporting/console.py",
    "tests/test_patterns.py",
]


def count_modules():
    return len([p for p in APPENDIX_ORDER if p.startswith("wealth/")])


def appendix():
    st = [PageBreak(), P("Appendix A   Source Code", "h1")]
    st += [P(
        "All modules of the project, in reading order. The package %s files, which only "
        "re-export names, are omitted." % C("__init__.py"))]
    for rel in APPENDIX_ORDER:
        lines = read(rel).rstrip("\n").splitlines()
        numbered = ["%3d  %s" % (i + 1, line) for i, line in enumerate(lines)]
        first = True
        for start in range(0, len(numbered), 80):
            block = listing("\n".join(numbered[start:start + 80]), fs="code_sm")
            if first:
                st.append(KeepTogether([P(rel, "file"), block]))
                first = False
            else:
                st.append(block)
        st.append(Spacer(1, 6))
    return st


def story():
    return (purpose() + theory() + requirements() + structure() + creational()
            + structural() + results() + discussion() + conclusions() + references()
            + appendix())
