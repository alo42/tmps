using WealthTracker.Domain;
using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Client;

/// <summary>
/// Measures what sharing saves: allocates the same number of lots twice,
/// once with pooled instruments and once with a fresh instrument per lot, and
/// compares the bytes allocated.
/// </summary>
public static class FlyweightMeasurement
{
    public sealed record Result(int Lots, int SharedInstruments, long SharedBytes, long UnsharedBytes)
    {
        public long SavedBytes => UnsharedBytes - SharedBytes;
        public decimal SavedPercent => UnsharedBytes == 0 ? 0 : (decimal)SavedBytes / UnsharedBytes * 100;
    }

    public static Result Run(int lots)
    {
        string[] symbols = ["AAPL", "MSFT", "VWCE", "BTC", "ETH", "EUR-CASH"];
        var catalog = InstrumentCatalog.Default();
        var factory = new InstrumentFactory(catalog);

        var shared = Allocated(lots, i => factory.Get(symbols[i % symbols.Length]));
        var unshared = Allocated(lots, i => catalog.Create(symbols[i % symbols.Length]));

        return new Result(lots, factory.Count, shared, unshared);
    }

    private static long Allocated(int count, Func<int, IInstrument> instrumentFor)
    {
        var day = new DateOnly(2024, 1, 1);
        GC.Collect();
        var before = GC.GetAllocatedBytesForCurrentThread();

        var lots = new Lot[count];
        for (var i = 0; i < count; i++)
            lots[i] = new Lot(instrumentFor(i), 1m, 100m, day);

        var after = GC.GetAllocatedBytesForCurrentThread();
        GC.KeepAlive(lots);
        return after - before;
    }
}
