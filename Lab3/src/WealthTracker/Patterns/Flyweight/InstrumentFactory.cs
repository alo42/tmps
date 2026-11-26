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

    // Created once. Passing the method group `catalog.Create` straight to
    // GetOrAdd would allocate a new delegate on every lookup - which cost more
    // memory than the shared instruments saved.
    private readonly Func<string, IInstrument> _create;

    public InstrumentFactory(InstrumentCatalog catalog)
    {
        _create = catalog.Create;
    }

    /// <summary>Number of distinct instruments created so far.</summary>
    public int Count => _pool.Count;

    public IInstrument Get(string symbol)
    {
        // Lookup-or-create. GetOrAdd is thread-safe: even if two threads race on
        // a new symbol, both receive the single instance that ends up stored.
        return _pool.GetOrAdd(symbol, _create);
    }
}
