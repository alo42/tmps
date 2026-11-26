# Lab 2 - Creational and Structural Design Patterns

Personal Wealth Dashboard & Multi-Asset Portfolio Tracker, continued from Lab 1
(SOLID). The single `wealth_dashboard.py` file from Lab 1 is split into a
package, and six design patterns are added.

```
python3 main.py              # run the dashboard (writes output/portfolio.csv|json)
python3 -m unittest -v       # 25 tests, one test class per pattern
python3 report/build_report.py   # rebuild Lab2_AdrianMutu_FAF-242.pdf
```

Python 3.9+, standard library only.

## Where each pattern lives

| Pattern | Category | Module | Classes |
|---|---|---|---|
| Singleton | Creational | `wealth/storage/database.py` | `Database` |
| Factory Method | Creational | `wealth/pricing/sources.py`, `wealth/assets/factory.py` | `MarketDataSource`, `DemoMarketData`, `LiveMarketData`; `AssetFactory` |
| Builder | Creational | `wealth/assets/builder.py` | `PortfolioBuilder`, `PortfolioDirector` |
| Composite | Structural | `wealth/assets/component.py`, `group.py`, `base.py` | `PortfolioComponent`, `AssetGroup`, `Asset` |
| Decorator | Structural | `wealth/valuation/fees.py` | `ValuationDecorator`, `PercentageFee`, `FixedFee` |
| Facade | Structural | `wealth/dashboard.py` | `WealthDashboard` |

## Layout

```
Lab2/
├── main.py                  client: uses only the facade and the director
├── wealth/
│   ├── money.py             Decimal helpers
│   ├── dashboard.py         FACADE
│   ├── assets/              COMPOSITE, BUILDER, FACTORY METHOD + asset types
│   ├── pricing/             price providers + FACTORY METHOD (sources)
│   ├── storage/             SINGLETON database + repository
│   ├── valuation/           calculator + DECORATOR fees
│   └── reporting/           CSV/JSON exporters, console rendering
├── tests/test_patterns.py
├── report/                  report generator: styles, uml, figures, content, build
└── Lab2_AdrianMutu_FAF-242.pdf
```
