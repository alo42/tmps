namespace WealthTracker.Domain;

/// <summary>
/// PROXY - the subject. Everything that reads or changes a portfolio depends on
/// this interface, so a proxy can be put in front of the real portfolio
/// without the caller noticing.
/// </summary>
public interface IPortfolio
{
    string Name { get; }
    IReadOnlyList<Lot> Lots { get; }

    void AddLot(Lot lot);
    bool RemoveLot(Lot lot);
}
