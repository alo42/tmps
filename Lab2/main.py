"""
Entry point. Thanks to the facade, the client needs only three names from the
package: the director that builds a portfolio, the dashboard that serves it,
and the market data source the dashboard is given.

Run:  python3 main.py
"""

import os

from wealth import DemoMarketData, PortfolioDirector, WealthDashboard

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def main() -> None:
    portfolio = PortfolioDirector().demo_portfolio()   # Builder + Composite
    dashboard = WealthDashboard(DemoMarketData())       # Facade + Factory Method
    dashboard.save_portfolio(portfolio)                  # Singleton database

    print(dashboard.report())                            # Decorator: "If sold"

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    written = [dashboard.export(os.path.join(OUTPUT_DIR, name))
               for name in ("portfolio.csv", "portfolio.json")]
    print("\nExported: " + ", ".join(os.path.relpath(p) for p in written))


if __name__ == "__main__":
    main()
