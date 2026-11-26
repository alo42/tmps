using WealthTracker.Domain;

namespace WealthTracker.Patterns.Flyweight;

/// <summary>
/// FLYWEIGHT - concrete flyweight. Immutable: every property is get-only and
/// set once in the constructor, so one instance can safely be shared by any
/// number of lots. The constructor is internal - clients obtain instances
/// through <see cref="InstrumentFactory"/>, never with <c>new</c>.
/// </summary>
public sealed class Instrument : IInstrument
{
    internal Instrument(string symbol, string name, AssetClass assetClass,
                        string exchange, string currency)
    {
        Symbol = symbol;
        Name = name;
        AssetClass = assetClass;
        Exchange = exchange;
        Currency = currency;
    }

    public string Symbol { get; }
    public string Name { get; }
    public AssetClass AssetClass { get; }
    public string Exchange { get; }
    public string Currency { get; }

    public decimal MarketValue(decimal quantity, IQuoteService quotes) =>
        quantity * quotes.PriceOf(Symbol);

    public override string ToString() => Symbol;
}
