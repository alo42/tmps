using WealthTracker.Domain;

namespace WealthTracker.Patterns.Bridge;

/// <summary>BRIDGE - refined abstraction: invested amount versus today's value.</summary>
public sealed class PerformanceReport : Report
{
    public PerformanceReport(IReportRenderer renderer) : base(renderer) { }

    protected override string Heading => "Performance";

    protected override string Body(IPortfolio portfolio, IQuoteService quotes)
    {
        var holdings = PortfolioValuation.Holdings(portfolio, quotes);
        var invested = holdings.Sum(h => h.CostBasis);
        var value = holdings.Sum(h => h.MarketValue);
        var gain = value - invested;
        var best = holdings.MaxBy(h => h.GainPercent);

        return Renderer.Field("Invested", Formats.Money(invested))
             + Renderer.Field("Market value", Formats.Money(value))
             + Renderer.Field("Unrealised gain", Formats.Money(gain))
             + Renderer.Field("Return", Formats.Percent(invested == 0 ? 0 : gain / invested * 100))
             + Renderer.Field("Best performer",
                   best is null ? "-" : $"{best.Instrument.Symbol} ({Formats.Percent(best.GainPercent)})");
    }
}
