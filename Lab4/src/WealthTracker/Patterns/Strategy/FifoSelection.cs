using WealthTracker.Domain;

namespace WealthTracker.Patterns.Strategy;

/// <summary>STRATEGY - concrete strategy: first in, first out - the oldest lots are sold first.</summary>
public sealed class FifoSelection : ILotSelectionStrategy
{
    public string Name => "FIFO";

    public IReadOnlyList<LotPick> Select(IReadOnlyList<Lot> lots, decimal quantity) =>
        LotPicking.TakeInOrder(lots.OrderBy(lot => lot.Purchased), quantity);
}
