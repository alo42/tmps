using WealthTracker.Domain;

namespace WealthTracker.Patterns.Bridge;

/// <summary>BRIDGE - refined abstraction: how the money is spread across asset classes.</summary>
public sealed class AllocationReport : Report
{
    public AllocationReport(IReportRenderer renderer) : base(renderer) { }

    protected override string Heading => "Allocation";

    protected override string Body(IPortfolio portfolio, IQuoteService quotes)
    {
        var allocation = PortfolioValuation.ByAssetClass(PortfolioValuation.Holdings(portfolio, quotes));
        Column[] columns = [new("Asset class"), new("Value", Numeric: true), new("Share", Numeric: true)];
        var rows = allocation.Select(a => (IReadOnlyList<string>)
        [
            a.AssetClass.ToString(), Formats.Money(a.MarketValue), Formats.Percent(a.SharePercent),
        ]);
        return Renderer.Table(columns, rows);
    }
}
