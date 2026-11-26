using WealthTracker.Domain;
using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Tests;

/// <summary>The demo portfolio, built by hand so tests do not depend on the builder.</summary>
internal static class TestData
{
    public const string TotalValue = "54,715.95";
    public const string TotalCost = "41,856.80";

    public static Portfolio DemoPortfolio(InstrumentFactory instruments)
    {
        var lots = new List<Lot>
        {
            new(instruments.Get("AAPL"), 8m, 150.00m, new DateOnly(2022, 3, 15)),
            new(instruments.Get("AAPL"), 4m, 185.20m, new DateOnly(2023, 6, 1)),
            new(instruments.Get("MSFT"), 5m, 310.00m, new DateOnly(2022, 11, 10)),
            new(instruments.Get("BTC"), 0.20m, 38_500m, new DateOnly(2023, 1, 20)),
            new(instruments.Get("BTC"), 0.15m, 52_000m, new DateOnly(2024, 2, 5)),
            new(instruments.Get("ETH"), 4.2m, 1_850m, new DateOnly(2023, 3, 12)),
            new(instruments.Get("EUR-CASH"), 7_500m, 1.00m, new DateOnly(2024, 9, 1)),
        };
        for (var month = 0; month < 36; month++)
            lots.Add(new Lot(instruments.Get("VWCE"), 2m, 95.00m + 0.60m * month,
                             new DateOnly(2022, 1, 5).AddMonths(month)));
        return new Portfolio("Adrian", lots);
    }
}
