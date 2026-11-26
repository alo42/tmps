using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;

namespace WealthTracker.Patterns.Observer;

/// <summary>
/// OBSERVER - concrete observer: warns when the instrument just traded makes up
/// more than <c>limitPercent</c> of the portfolio's value - too many eggs in one basket.
/// </summary>
public sealed class ConcentrationAlert : ITradeObserver
{
    private readonly IQuoteService _quotes;
    private readonly decimal _limitPercent;
    private readonly TextWriter _output;
    private readonly List<string> _alerts = [];

    public ConcentrationAlert(IQuoteService quotes, decimal limitPercent, TextWriter output)
    {
        _quotes = quotes;
        _limitPercent = limitPercent;
        _output = output;
    }

    public IReadOnlyList<string> Alerts => _alerts;

    public void OnTrade(TradeEvent change)
    {
        var holdings = PortfolioValuation.Holdings(change.Lots, _quotes);
        var total = holdings.Sum(h => h.MarketValue);
        var holding = holdings.FirstOrDefault(h => h.Instrument == change.Trade.Instrument);
        if (holding is null || total == 0)
            return;
        var share = holding.MarketValue / total * 100;
        if (share <= _limitPercent)
            return;
        var alert = $"{holding.Instrument.Symbol} is {Formats.Percent(share)} of the portfolio, above the {Formats.Quantity(_limitPercent)}% limit";
        _alerts.Add(alert);
        _output.WriteLine($"  [alert]  {alert}");
    }
}
