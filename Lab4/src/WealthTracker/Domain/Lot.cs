using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Domain;

/// <summary>
/// One purchase of an instrument. FLYWEIGHT - context: stores only the
/// extrinsic state (how much, at what price, when) plus a reference to the
/// shared <see cref="IInstrument"/>.
/// </summary>
public sealed class Lot
{
    public Lot(IInstrument instrument, decimal quantity, decimal unitCost, DateOnly purchased)
    {
        ArgumentNullException.ThrowIfNull(instrument);
        if (quantity <= 0)
            throw new ArgumentOutOfRangeException(nameof(quantity), "Quantity must be positive.");
        if (unitCost < 0)
            throw new ArgumentOutOfRangeException(nameof(unitCost), "Unit cost cannot be negative.");

        Instrument = instrument;
        Quantity = quantity;
        UnitCost = unitCost;
        Purchased = purchased;
    }

    public IInstrument Instrument { get; }
    public decimal Quantity { get; }
    public decimal UnitCost { get; }
    public DateOnly Purchased { get; }

    public decimal CostBasis => Quantity * UnitCost;

    /// <summary>Passes the extrinsic quantity to the shared flyweight.</summary>
    public decimal MarketValue(IQuoteService quotes) => Instrument.MarketValue(Quantity, quotes);
}
