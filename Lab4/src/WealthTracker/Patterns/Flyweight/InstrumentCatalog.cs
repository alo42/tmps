using WealthTracker.Domain;

namespace WealthTracker.Patterns.Flyweight;

/// <summary>
/// Reference data for every tradable instrument, as a market-data vendor would
/// supply it. In a real system a lookup here is a database query or an API
/// call - one more reason to perform it once per symbol, not once per lot.
/// </summary>
public sealed class InstrumentCatalog
{
    private readonly Dictionary<string, (string Name, AssetClass AssetClass, string Exchange, string Currency)> _rows;
    private int _lookups;

    public InstrumentCatalog(
        IEnumerable<(string Symbol, string Name, AssetClass AssetClass, string Exchange, string Currency)> rows)
    {
        _rows = rows.ToDictionary(r => r.Symbol, r => (r.Name, r.AssetClass, r.Exchange, r.Currency),
                                  StringComparer.OrdinalIgnoreCase);
    }

    /// <summary>How many times an instrument was built from the catalog.</summary>
    public int Lookups => _lookups;

    /// <summary>Builds a new, unshared instrument. The factory calls this at most once per symbol.</summary>
    public IInstrument Create(string symbol)
    {
        if (!_rows.TryGetValue(symbol, out var row))
            throw new KeyNotFoundException($"Unknown instrument '{symbol}'.");
        Interlocked.Increment(ref _lookups);
        return new Instrument(symbol.ToUpperInvariant(), row.Name, row.AssetClass, row.Exchange, row.Currency);
    }

    public static InstrumentCatalog Default() => new(
    [
        ("AAPL", "Apple Inc.", AssetClass.Stock, "NASDAQ", "USD"),
        ("MSFT", "Microsoft Corp.", AssetClass.Stock, "NASDAQ", "USD"),
        ("VWCE", "Vanguard FTSE All-World UCITS ETF", AssetClass.Etf, "XETRA", "EUR"),
        ("BTC", "Bitcoin", AssetClass.Crypto, "Kraken", "EUR"),
        ("ETH", "Ethereum", AssetClass.Crypto, "Kraken", "EUR"),
        ("EUR-CASH", "Savings account", AssetClass.Cash, "maib", "EUR"),
    ]);
}
