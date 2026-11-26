using WealthTracker.Domain;

namespace WealthTracker.Patterns.Observer;

public enum TradeEventKind
{
    /// <summary>The trade was made (or redone).</summary>
    Executed,

    /// <summary>The trade was undone.</summary>
    Reversed,
}

/// <summary>
/// What observers receive: the trade, whether it was made or undone, and a
/// read-only view of the portfolio's lots after the change. Observers can look
/// at the portfolio but not change it.
/// </summary>
public sealed record TradeEvent(TradeEventKind Kind, Trade Trade, IReadOnlyList<Lot> Lots);
