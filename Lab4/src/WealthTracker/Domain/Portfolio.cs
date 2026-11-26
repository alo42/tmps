using System.Collections.ObjectModel;

namespace WealthTracker.Domain;

/// <summary>PROXY - the real subject: an in-memory list of purchase lots.</summary>
public sealed class Portfolio : IPortfolio
{
    private readonly List<Lot> _lots;
    private readonly ReadOnlyCollection<Lot> _view;

    public Portfolio(string name, IEnumerable<Lot>? lots = null)
    {
        Name = name;
        _lots = lots?.ToList() ?? [];
        _view = _lots.AsReadOnly();
    }

    public string Name { get; }

    /// <summary>A live, read-only view: callers can see the lots but not change the list.</summary>
    public IReadOnlyList<Lot> Lots => _view;

    public void AddLot(Lot lot)
    {
        ArgumentNullException.ThrowIfNull(lot);
        _lots.Add(lot);
    }

    public bool RemoveLot(Lot lot) => _lots.Remove(lot);
}
