using WealthTracker.Domain;

namespace WealthTracker.Creational;

/// <summary>BUILDER - director: owns the recipe for a named portfolio.</summary>
public sealed class PortfolioDirector
{
    private readonly PortfolioBuilder _builder;

    public PortfolioDirector(PortfolioBuilder builder)
    {
        _builder = builder;
    }

    /// <summary>The Lab 1 holdings, now as dated purchase lots, plus a 3-year ETF savings plan.</summary>
    public IPortfolio BuildDemo() => _builder
        .Named("Adrian")
        .Buy("AAPL", 8m, 150.00m, new DateOnly(2022, 3, 15))
        .Buy("AAPL", 4m, 185.20m, new DateOnly(2023, 6, 1))
        .Buy("MSFT", 5m, 310.00m, new DateOnly(2022, 11, 10))
        .Buy("BTC", 0.20m, 38_500m, new DateOnly(2023, 1, 20))
        .Buy("BTC", 0.15m, 52_000m, new DateOnly(2024, 2, 5))
        .Buy("ETH", 4.2m, 1_850m, new DateOnly(2023, 3, 12))
        .Buy("EUR-CASH", 7_500m, 1.00m, new DateOnly(2024, 9, 1))
        .BuyMonthly("VWCE", 2m, firstCost: 95.00m, monthlyCostChange: 0.60m,
                    start: new DateOnly(2022, 1, 5), months: 36)
        .Build();
}
