namespace WealthTracker.Domain;

/// <summary>
/// Exactly what a trade changed in the portfolio: the lots it added and the lots
/// it removed. Lots are immutable, so applying a receipt backwards restores the
/// portfolio to the state it had before the trade.
/// </summary>
public sealed record TradeReceipt(Trade Trade, IReadOnlyList<Lot> Added, IReadOnlyList<Lot> Removed);
