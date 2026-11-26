using WealthTracker.Domain;

namespace WealthTracker.Patterns.Strategy;

/// <summary>STRATEGY - concrete strategy: last in, first out - the newest lots are sold first.</summary>
public sealed class LifoSelection : ILotSelectionStrategy
{
    public string Name => "LIFO";

    public IReadOnlyList<LotPick> Select(IReadOnlyList<Lot> lots, decimal quantity) =>
        LotPicking.TakeInOrder(lots.OrderByDescending(lot => lot.Purchased), quantity);
}
