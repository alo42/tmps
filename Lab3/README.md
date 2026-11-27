# Lab 3 — Structural Design Patterns (C#)

**Personal Wealth Dashboard & Multi-Asset Portfolio Tracker**, continued from
Labs 1–2. Implements **Flyweight**, **Proxy** and **Bridge**, reusing the
**Builder** and **Factory Method** from Lab 2 to create the objects they work with.

The report is in [REPORT.md](REPORT.md) (also as [PDF](Lab3_AdrianMutu_FAF-242.pdf)).

## Requirements

- [.NET SDK 10](https://dotnet.microsoft.com/download) — nothing else.

## Build, run, test

Run from this folder (`Lab3/`):

```bash
dotnet build                                      # compile app + tests
dotnet run --project src/WealthTracker            # demo, holdings report as a console table
dotnet run --project src/WealthTracker -- markdown   # ... or: console | markdown | csv
dotnet run --project src/WealthTracker -- shell      # try the Flyweight and the Proxy live
dotnet test                                       # all 32 unit tests, one command
dotnet test --output Detailed                     # ... listing every test
```

## Live mode — Flyweight and Proxy while you type

`dotnet run --project src/WealthTracker -- shell` opens the demo portfolio for
typed commands. Every purchase first shows what the **Flyweight** factory did
(reused an instrument object or created one), then what the **Proxy** decided
for the current user.

| Command | Shows |
|---|---|
| `pool` | every shared instrument object and how many lots use it |
| `buy SYMBOL QTY [PRICE]` | Flyweight: existing or NEW object; Proxy: ALLOWED or DENIED |
| `sell SYMBOL` | removes the newest lot of SYMBOL through the proxy |
| `lots SYMBOL` | each lot and the instrument object it points to |
| `as adrian` / `as ion` / `as guest` | switch user: Owner, Advisor (view only), Guest (nothing) |
| `report [console\|markdown\|csv]`, `log` | the holdings report and the access log, through the current user's proxy |

`#A42D` is the object's identity in memory — the same id means the very same
object (ids change from run to run). `NVDA` is in the catalog but not in the
portfolio, so its first purchase is the one that creates a new object:

```text
Adrian> buy VWCE 2
  flyweight  VWCE -> existing object #A42D  (nothing created)   pool: 6 objects, catalog reads: 6
  proxy      ALLOWED  Adrian bought 2 VWCE @ 118.40
Adrian> buy NVDA 3
  flyweight  NVDA -> NEW object #C59A  (first request: read from the catalog)   pool: 7 objects, catalog reads: 7
  proxy      ALLOWED  Adrian bought 3 NVDA @ 182.30
Adrian> buy 1 NVDA
  flyweight  NVDA -> existing object #C59A  (nothing created)   pool: 7 objects, catalog reads: 7
  proxy      ALLOWED  Adrian bought 1 NVDA @ 182.30
Adrian> as ion
  now acting as Ion (Advisor) - permissions: View
Ion> buy AAPL 1
  flyweight  AAPL -> existing object #3390  (nothing created)   pool: 7 objects, catalog reads: 7
  proxy      DENIED   Ion (Advisor) is not allowed to buy 1 AAPL.  (the real portfolio was not touched)
Ion> as guest
  now acting as Visitor (Guest) - permissions: None
Visitor> lots BTC
  proxy      DENIED   Visitor (Guest) is not allowed to view the lots.  (the real portfolio was not touched)
```

## Where each pattern lives

| Pattern | Role | Class | File |
|---|---|---|---|
| **Flyweight** | Flyweight | `IInstrument` | [Patterns/Flyweight/IInstrument.cs](src/WealthTracker/Patterns/Flyweight/IInstrument.cs) |
| | Concrete flyweight | `Instrument` | [Patterns/Flyweight/Instrument.cs](src/WealthTracker/Patterns/Flyweight/Instrument.cs) |
| | Flyweight factory | `InstrumentFactory` | [Patterns/Flyweight/InstrumentFactory.cs](src/WealthTracker/Patterns/Flyweight/InstrumentFactory.cs) |
| | Context (extrinsic state) | `Lot` | [Domain/Lot.cs](src/WealthTracker/Domain/Lot.cs) |
| **Proxy** | Subject | `IPortfolio` | [Domain/IPortfolio.cs](src/WealthTracker/Domain/IPortfolio.cs) |
| | Real subject | `Portfolio` | [Domain/Portfolio.cs](src/WealthTracker/Domain/Portfolio.cs) |
| | Proxy | `PortfolioAccessProxy` | [Patterns/Proxy/PortfolioAccessProxy.cs](src/WealthTracker/Patterns/Proxy/PortfolioAccessProxy.cs) |
| **Bridge** | Abstraction | `Report` | [Patterns/Bridge/Report.cs](src/WealthTracker/Patterns/Bridge/Report.cs) |
| | Refined abstractions | `HoldingsReport`, `AllocationReport`, `PerformanceReport` | [Patterns/Bridge/](src/WealthTracker/Patterns/Bridge/) |
| | Implementor | `IReportRenderer` | [Patterns/Bridge/IReportRenderer.cs](src/WealthTracker/Patterns/Bridge/IReportRenderer.cs) |
| | Concrete implementors | `ConsoleTableRenderer`, `MarkdownRenderer`, `CsvRenderer` | [Patterns/Bridge/](src/WealthTracker/Patterns/Bridge/) |
| Builder *(Lab 2)* | Builder / Director | `PortfolioBuilder`, `PortfolioDirector` | [Creational/](src/WealthTracker/Creational/) |
| Factory Method *(Lab 2)* | Parameterised factory | `RendererFactory` | [Creational/RendererFactory.cs](src/WealthTracker/Creational/RendererFactory.cs) |

## Project layout

```
Lab3/
├── WealthTracker.slnx          solution (dotnet build / dotnet test use it)
├── global.json                 runs tests on Microsoft.Testing.Platform
├── src/WealthTracker/
│   ├── Program.cs              entry point
│   ├── Client/                 client code: console demo, live shell, Flyweight measurement
│   ├── Domain/                 domain models: Lot, Portfolio, IPortfolio, quotes, valuation
│   ├── Patterns/
│   │   ├── Flyweight/          IInstrument, Instrument, InstrumentFactory, InstrumentCatalog
│   │   ├── Proxy/              PortfolioAccessProxy, User, Role, Permission, ...
│   │   └── Bridge/             Report + 3 reports, IReportRenderer + 3 renderers
│   └── Creational/             PortfolioBuilder, PortfolioDirector, RendererFactory
├── tests/WealthTracker.Tests/  32 xUnit v3 tests, one class per pattern
├── docs/                       captured test log and demo output
│   └── report-builder/         renders REPORT.md into the PDF (see below)
├── REPORT.md                   the report
└── Lab3_AdrianMutu_FAF-242.pdf the same report with the UTM cover page
```

The application and its tests are C# only. `docs/report-builder/` is
documentation tooling (Python + ReportLab) that turns `REPORT.md` into the PDF:
`python3 docs/report-builder/build_pdf.py`.

## Extending it — new classes only

| To add… | Write… | Then… |
|---|---|---|
| an output format (e.g. HTML) | `HtmlRenderer : IReportRenderer` | `RendererFactory.Default().Register("html", () => new HtmlRenderer())` |
| a report (e.g. dividends) | `DividendReport : Report` | use it with any renderer |
| a role (e.g. auditor) | nothing | `new Role("Auditor", Permission.View)` |
| an instrument | a row in `InstrumentCatalog` (data) | `factory.Get("NEWSYM")` |

No existing class changes in any of these cases; the tests
`NewRenderer_…`, `NewReport_…`, `NewRole_…` and `RendererFactory_NewFormat_…`
demonstrate it.
