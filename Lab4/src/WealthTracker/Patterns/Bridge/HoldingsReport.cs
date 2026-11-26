using WealthTracker.Domain;

namespace WealthTracker.Patterns.Bridge;

/// <summary>BRIDGE - refined abstraction: one row per instrument.</summary>
public sealed class HoldingsReport : Report
{
    public HoldingsReport(IReportRenderer renderer) : base(renderer) { }

    protected override string Heading => "Holdings";

    protected override string Body(IPortfolio portfolio, IQuoteService quotes)
    {
        var holdings = PortfolioValuation.Holdings(portfolio, quotes);
        Column[] columns =
        [
            new("Symbol"), new("Name"), new("Quantity", Numeric: true),
            new("Cost", Numeric: true), new("Value", Numeric: true), new("Gain", Numeric: true),
        ];
        var rows = holdings.Select(h => (IReadOnlyList<string>)
        [
            h.Instrument.Symbol, h.Instrument.Name, Formats.Quantity(h.Quantity),
            Formats.Money(h.CostBasis), Formats.Money(h.MarketValue), Formats.Percent(h.GainPercent),
        ]);
        return Renderer.Table(columns, rows)
             + Renderer.Field("Total value", Formats.Money(holdings.Sum(h => h.MarketValue)));
    }
}
