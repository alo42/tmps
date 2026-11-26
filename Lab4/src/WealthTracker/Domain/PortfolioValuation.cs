using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Domain;

/// <summary>All lots of one instrument, added together.</summary>
public sealed record Holding(IInstrument Instrument, decimal Quantity, decimal CostBasis, decimal MarketValue)
{
    public decimal Gain => MarketValue - CostBasis;
    public decimal GainPercent => CostBasis == 0 ? 0 : Gain / CostBasis * 100;
}

/// <summary>Value of one asset class and its share of the whole portfolio.</summary>
public sealed record Allocation(AssetClass AssetClass, decimal MarketValue, decimal SharePercent);

/// <summary>
/// Pure calculations over a portfolio. Reports call these and only decide how
/// the results look, which keeps arithmetic out of the presentation code.
/// </summary>
public static class PortfolioValuation
{
    public static IReadOnlyList<Holding> Holdings(IPortfolio portfolio, IQuoteService quotes) =>
        Holdings(portfolio.Lots, quotes);

    public static IReadOnlyList<Holding> Holdings(IEnumerable<Lot> lots, IQuoteService quotes) =>
        lots
            // Flyweights are shared, so grouping by the instrument reference
            // puts every lot of the same symbol in one group.
            .GroupBy(lot => lot.Instrument)
            .Select(group =>
            {
                var quantity = group.Sum(lot => lot.Quantity);
                return new Holding(group.Key, quantity, group.Sum(lot => lot.CostBasis),
                                   group.Key.MarketValue(quantity, quotes));
            })
            .OrderByDescending(h => h.MarketValue)
            .ToList();

    public static IReadOnlyList<Allocation> ByAssetClass(IReadOnlyList<Holding> holdings)
    {
        var total = holdings.Sum(h => h.MarketValue);
        return holdings
            .GroupBy(h => h.Instrument.AssetClass)
            .Select(g => new Allocation(g.Key, g.Sum(h => h.MarketValue),
                                        total == 0 ? 0 : g.Sum(h => h.MarketValue) / total * 100))
            .OrderByDescending(a => a.MarketValue)
            .ToList();
    }
}
