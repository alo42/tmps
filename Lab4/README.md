# Lab 4 — Behavioral Design Patterns (C#)

**Personal Wealth Dashboard & Multi-Asset Portfolio Tracker**, continued from
Labs 1–3. Adds trading with **Strategy** (which lots a sale uses), **Command**
(trades with undo/redo) and **Observer** (log, realised gains and alerts react
to every trade), built on Lab 3's Flyweight, Proxy and Bridge and Lab 2's
Builder and Factory Method.

The report is in [REPORT.md](REPORT.md) (also as [PDF](Lab4_AdrianMutu_FAF-242.pdf)).

## Requirements

- [.NET SDK 10](https://dotnet.microsoft.com/download) — nothing else.

## Build, run, test

Run from this folder (`Lab4/`):

```bash
dotnet build                                       # compile app + tests
dotnet run --project src/WealthTracker             # scripted demo of every pattern
dotnet run --project src/WealthTracker -- shell    # type the commands yourself
dotnet test                                        # all 60 unit tests, one command
dotnet test --output Detailed                      # ... listing every test
```

## Shell commands

The demo is a scripted session of these commands; in `-- shell` mode you type them.

| Command | What it does | Pattern |
|---|---|---|
| `buy SYMBOL QTY [PRICE] [YYYY-MM-DD]` | records a purchase (price defaults to the current quote, date to today) | Command |
| `sell SYMBOL QTY [PRICE] [YYYY-MM-DD]` | records a sale; the current lot-selection method picks the lots | Command + Strategy |
| `undo` / `redo` / `history` | step back, step forward, list the trades in effect | Command |
| `method [fifo\|lifo\|hifo]` | show or switch the lot-selection method while the program runs | Strategy |
| `watch` / `unwatch [log\|gains\|alerts]` | subscribe or unsubscribe an observer while the program runs | Observer |
| `holdings` | holdings report | Bridge |
| `help`, `quit` | | |

Commands are case-insensitive, and the quantity may come before the symbol: `SELL 2 AAPL` is the same as `sell AAPL 2`.

Example: `method hifo`, then `sell ETH 2` realises −1,038.50 instead of +2,261.50 under FIFO.

## Where each pattern lives

| Pattern | Role | Class | File |
|---|---|---|---|
| **Strategy** | Strategy | `ILotSelectionStrategy` | [Patterns/Strategy/ILotSelectionStrategy.cs](src/WealthTracker/Patterns/Strategy/ILotSelectionStrategy.cs) |
| | Concrete strategies | `FifoSelection`, `LifoSelection`, `HighestCostSelection` | [Patterns/Strategy/](src/WealthTracker/Patterns/Strategy/) |
| | Context | `TradingAccount` | [Domain/TradingAccount.cs](src/WealthTracker/Domain/TradingAccount.cs) |
| **Command** | Command | `ITradeCommand` (+ base `TradeCommand`) | [Patterns/Command/](src/WealthTracker/Patterns/Command/) |
| | Concrete commands | `BuyCommand`, `SellCommand` | [Patterns/Command/](src/WealthTracker/Patterns/Command/) |
| | Receiver | `TradingAccount` | [Domain/TradingAccount.cs](src/WealthTracker/Domain/TradingAccount.cs) |
| | Invoker | `TradeHistory` | [Patterns/Command/TradeHistory.cs](src/WealthTracker/Patterns/Command/TradeHistory.cs) |
| | Client | `TradeShell` | [Client/TradeShell.cs](src/WealthTracker/Client/TradeShell.cs) |
| **Observer** | Subject | `ITradeSubject` → `TradingAccount` | [Patterns/Observer/ITradeSubject.cs](src/WealthTracker/Patterns/Observer/ITradeSubject.cs) |
| | Observer | `ITradeObserver` | [Patterns/Observer/ITradeObserver.cs](src/WealthTracker/Patterns/Observer/ITradeObserver.cs) |
| | Concrete observers | `ActivityLog`, `RealisedGainsTracker`, `ConcentrationAlert` | [Patterns/Observer/](src/WealthTracker/Patterns/Observer/) |
| Flyweight, Proxy, Bridge *(Lab 3)* | | | [Patterns/](src/WealthTracker/Patterns/) |
| Builder, Factory Method *(Lab 2)* | | `PortfolioBuilder`, `RendererFactory`, `LotSelectionFactory` | [Creational/](src/WealthTracker/Creational/) |

## Project layout

```
Lab4/
├── WealthTracker.slnx          solution (dotnet build / dotnet test use it)
├── global.json                 runs tests on Microsoft.Testing.Platform
├── src/WealthTracker/
│   ├── Program.cs              entry point: demo, or "shell"
│   ├── Client/                 ConsoleDemo, TradeShell, FlyweightMeasurement
│   ├── Domain/                 Lot, Portfolio, TradingAccount, Trade, TradeReceipt, ...
│   ├── Patterns/
│   │   ├── Strategy/           lot-selection methods
│   │   ├── Command/            trade commands + history
│   │   ├── Observer/           trade notifications
│   │   ├── Flyweight/          (Lab 3)
│   │   ├── Proxy/              (Lab 3)
│   │   └── Bridge/             (Lab 3)
│   └── Creational/             PortfolioBuilder, PortfolioDirector, RendererFactory, LotSelectionFactory
├── tests/WealthTracker.Tests/  60 xUnit v3 tests, one class per pattern
├── docs/                       captured test log and demo output
│   └── report-builder/         renders REPORT.md into the PDF
├── REPORT.md                   the report
└── Lab4_AdrianMutu_FAF-242.pdf the same report with the UTM cover page
```

The application and its tests are C# only. `docs/report-builder/` is
documentation tooling (Python + ReportLab) that turns `REPORT.md` into the PDF:
`python3 docs/report-builder/build_pdf.py`.

## Extending it — new classes only

| To add… | Write… | Then… |
|---|---|---|
| a lot-selection method (e.g. lowest cost first) | `LowestCostSelection : ILotSelectionStrategy` | `LotSelectionFactory.Default().Register("lofo", () => new LowestCostSelection())` |
| a trade command (e.g. a savings plan: several buys as one step) | `SavingsPlanCommand : ITradeCommand` that runs its `BuyCommand`s and undoes them in reverse | `history.Execute(new SavingsPlanCommand(...))` — undo/redo work unchanged |
| a reaction to trades (e.g. an e-mail) | `EmailNotifier : ITradeObserver` | `account.Subscribe(new EmailNotifier(...))` |

No existing class changes in these cases; the tests `NewMethod_PlugsIn_…`,
`History_RunsAnyITradeCommand` and the spy observers in `ObserverTests` show it.
