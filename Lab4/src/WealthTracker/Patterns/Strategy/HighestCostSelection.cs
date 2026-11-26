using WealthTracker.Domain;

namespace WealthTracker.Patterns.Strategy;

/// <summary>
/// STRATEGY - concrete strategy: highest cost first (HIFO). Selling the most
/// expensive units first gives the smallest taxable gain - or a loss.
/// </summary>
public sealed class HighestCostSelection : ILotSelectionStrategy
{
    public string Name => "HIFO";

    public IReadOnlyList<LotPick> Select(IReadOnlyList<Lot> lots, decimal quantity) =>
        LotPicking.TakeInOrder(lots.OrderByDescending(lot => lot.UnitCost).ThenBy(lot => lot.Purchased), quantity);
}
