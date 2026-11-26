using WealthTracker.Domain;

namespace WealthTracker.Patterns.Flyweight;

/// <summary>
/// FLYWEIGHT - the interface. Exposes the intrinsic (shared) state of an
/// instrument. Anything that differs per purchase - such as the quantity - is
/// extrinsic and is passed in as a parameter, never stored.
/// </summary>
public interface IInstrument
{
    string Symbol { get; }
    string Name { get; }
    AssetClass AssetClass { get; }
    string Exchange { get; }
    string Currency { get; }

    /// <summary>Value of <paramref name="quantity"/> units at the current price.</summary>
    decimal MarketValue(decimal quantity, IQuoteService quotes);
}
