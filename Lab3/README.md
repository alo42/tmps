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
dotnet test                                       # all 31 unit tests, one command
dotnet test --output Detailed                     # ... listing every test
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
│   ├── Client/                 client code: the console demo + Flyweight measurement
│   ├── Domain/                 domain models: Lot, Portfolio, IPortfolio, quotes, valuation
│   ├── Patterns/
│   │   ├── Flyweight/          IInstrument, Instrument, InstrumentFactory, InstrumentCatalog
│   │   ├── Proxy/              PortfolioAccessProxy, User, Role, Permission, ...
│   │   └── Bridge/             Report + 3 reports, IReportRenderer + 3 renderers
│   └── Creational/             PortfolioBuilder, PortfolioDirector, RendererFactory
├── tests/WealthTracker.Tests/  31 xUnit v3 tests, one class per pattern
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
