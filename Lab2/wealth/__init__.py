"""
Personal Wealth Dashboard & Multi-Asset Portfolio Tracker - Lab 2.

Most clients only need the facade and the director:

    from wealth import PortfolioDirector, WealthDashboard

    dashboard = WealthDashboard()
    dashboard.save_portfolio(PortfolioDirector().demo_portfolio())
    print(dashboard.report())
"""

from wealth.assets import PortfolioBuilder, PortfolioDirector
from wealth.dashboard import DashboardSummary, WealthDashboard
from wealth.pricing import DemoMarketData, LiveMarketData

__all__ = ["DashboardSummary", "DemoMarketData", "LiveMarketData",
           "PortfolioBuilder", "PortfolioDirector", "WealthDashboard"]
