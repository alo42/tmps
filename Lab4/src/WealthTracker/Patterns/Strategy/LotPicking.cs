using WealthTracker.Domain;

namespace WealthTracker.Patterns.Strategy;

/// <summary>Shared step for strategies that consume lots in a fixed order.</summary>
public static class LotPicking
{
    /// <summary>Takes whole lots in the given order and only part of the last one.</summary>
    public static IReadOnlyList<LotPick> TakeInOrder(IEnumerable<Lot> orderedLots, decimal quantity)
    {
        var picks = new List<LotPick>();
        var remaining = quantity;
        foreach (var lot in orderedLots)
        {
            if (remaining == 0)
                break;
            var take = Math.Min(lot.Quantity, remaining);
            picks.Add(new LotPick(lot, take));
            remaining -= take;
        }
        if (remaining > 0)
            throw new InvalidOperationException(FormattableString.Invariant($"The lots hold {quantity - remaining} units; {quantity} were requested."));
        return picks;
    }
}
