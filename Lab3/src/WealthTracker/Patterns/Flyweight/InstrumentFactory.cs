using System.Collections.Concurrent;

namespace WealthTracker.Patterns.Flyweight;

/// <summary>
/// FLYWEIGHT - the factory. Returns the existing instrument for a symbol, or
/// creates and pools it on first request. Every lot of the same symbol
/// therefore points at one shared object.
/// </summary>
public sealed class InstrumentFactory
{
    private readonly ConcurrentDictionary<string, IInstrument> _pool = new(StringComparer.OrdinalIgnoreCase);
    private readonly InstrumentCatalog _catalog;

    public InstrumentFactory(InstrumentCatalog catalog)
    {
        _catalog = catalog;
    }

    /// <summary>Number of distinct instruments created so far.</summary>
    public int Count => _pool.Count;

    public IInstrument Get(string symbol)
    {
        // Lookup-or-create. GetOrAdd is thread-safe: even if two threads race on
        // a new symbol, both receive the single instance that ends up stored.
        return _pool.GetOrAdd(symbol, _catalog.Create);
    }
}
