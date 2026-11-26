using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;

namespace WealthTracker.Patterns.Observer;

/// <summary>OBSERVER - concrete observer: a readable line for every trade and undo.</summary>
public sealed class ActivityLog : ITradeObserver
{
    private readonly TextWriter _output;
    private readonly List<string> _entries = [];

    public ActivityLog(TextWriter output)
    {
        _output = output;
    }

    public IReadOnlyList<string> Entries => _entries;

    public void OnTrade(TradeEvent change)
    {
        var entry = (change.Kind == TradeEventKind.Reversed ? "UNDONE " : "") + Describe(change.Trade);
        _entries.Add(entry);
        _output.WriteLine($"  [log]    {entry}");
    }

    private static string Describe(Trade trade)
    {
        var text = $"{trade.Side.ToString().ToUpperInvariant()} {Formats.Quantity(trade.Quantity)} " +
                   $"{trade.Instrument.Symbol} @ {Formats.Money(trade.Price)} on {trade.Date:yyyy-MM-dd}";
        if (trade.Side == TradeSide.Buy)
            return text;
        var lots = trade.Picks.Select(p =>
            $"{Formats.Quantity(p.Quantity)} from {p.Lot.Purchased:yyyy-MM-dd} @ {Formats.Money(p.Lot.UnitCost)}");
        return $"{text} - {trade.Method}: {string.Join(", ", lots)}";
    }
}
