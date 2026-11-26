using WealthTracker.Domain;

namespace WealthTracker.Patterns.Strategy;

/// <summary>
/// STRATEGY - the strategy interface. When only part of a holding is sold, a
/// method decides which purchase lots the sold units come from. The choice
/// changes the realised gain - and therefore the tax - of the same sale.
/// </summary>
public interface ILotSelectionStrategy
{
    /// <summary>Short name shown to the user, e.g. "FIFO".</summary>
    string Name { get; }

    /// <summary>
    /// Chooses lots that together cover <paramref name="quantity"/> units.
    /// <paramref name="lots"/> are all lots of one instrument and hold at least that much.
    /// </summary>
    IReadOnlyList<LotPick> Select(IReadOnlyList<Lot> lots, decimal quantity);
}
