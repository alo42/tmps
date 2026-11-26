using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Domain;

public enum TradeSide
{
    Buy,
    Sell,
}

/// <summary>One executed buy or sell order.</summary>
public sealed record Trade(TradeSide Side, IInstrument Instrument, decimal Quantity, decimal Price, DateOnly Date)
{
    /// <summary>For a sale: the lots the sold units came from.</summary>
    public IReadOnlyList<LotPick> Picks { get; init; } = [];

    /// <summary>For a sale: the name of the lot-selection method that chose the lots.</summary>
    public string? Method { get; init; }

    /// <summary>Sale price minus purchase cost of the units sold; zero for a purchase.</summary>
    public decimal RealisedGain => Picks.Sum(p => p.Quantity * (Price - p.Lot.UnitCost));
}
