using System.Reflection;
using WealthTracker.Client;
using WealthTracker.Domain;
using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Tests;

public class FlyweightTests
{
    private static readonly DateOnly Day = new(2024, 1, 15);

    [Fact]
    public void Get_SameSymbolTwice_ReturnsTheSameInstance()
    {
        var factory = new InstrumentFactory(InstrumentCatalog.Default());

        var first = factory.Get("AAPL");
        var second = factory.Get("aapl");

        Assert.Same(first, second);
        Assert.Equal(1, factory.Count);
    }

    [Fact]
    public void TenThousandLots_ShareOneInstrumentPerSymbol()
    {
        var catalog = InstrumentCatalog.Default();
        var factory = new InstrumentFactory(catalog);
        string[] symbols = ["VWCE", "BTC", "AAPL"];

        var lots = Enumerable.Range(0, 10_000)
            .Select(i => new Lot(factory.Get(symbols[i % symbols.Length]), 1m, 100m, Day))
            .ToList();

        Assert.Equal(3, factory.Count);   // 3 flyweights for 10,000 lots
        Assert.Equal(3, catalog.Lookups); // reference data read once per symbol
        var vwce = lots[0].Instrument;
        Assert.All(lots.Where(l => l.Instrument.Symbol == "VWCE"), l => Assert.Same(vwce, l.Instrument));
    }

    [Fact]
    public void Instrument_IntrinsicStateIsImmutable()
    {
        var properties = typeof(Instrument).GetProperties(BindingFlags.Public | BindingFlags.Instance);
        var fields = typeof(Instrument).GetFields(BindingFlags.NonPublic | BindingFlags.Instance);

        Assert.All(properties, p => Assert.False(p.CanWrite, $"{p.Name} has a setter"));
        Assert.All(fields, f => Assert.True(f.IsInitOnly, $"{f.Name} is not readonly"));
    }

    [Fact]
    public void MarketValue_TakesQuantityAsExtrinsicState()
    {
        var quotes = InMemoryQuoteService.Demo();
        var btc = new InstrumentFactory(InstrumentCatalog.Default()).Get("BTC");

        var early = new Lot(btc, 0.20m, 38_500m, new DateOnly(2023, 1, 20));
        var late = new Lot(btc, 0.15m, 52_000m, new DateOnly(2024, 2, 5));

        Assert.Same(early.Instrument, late.Instrument);
        Assert.Equal(12_250.00m, early.MarketValue(quotes));
        Assert.Equal(9_187.50m, late.MarketValue(quotes));
    }

    [Fact]
    public void Get_FromManyThreadsAtOnce_StillCreatesOneInstance()
    {
        var factory = new InstrumentFactory(InstrumentCatalog.Default());
        var seen = new System.Collections.Concurrent.ConcurrentBag<IInstrument>();

        Parallel.For(0, 1_000, _ => seen.Add(factory.Get("ETH")));

        Assert.Single(seen.Distinct());
    }

    [Fact]
    public void SharingInstruments_AllocatesLessThanOneInstrumentPerLot()
    {
        var result = FlyweightMeasurement.Run(20_000);

        Assert.Equal(6, result.SharedInstruments);
        Assert.True(result.SavedPercent > 30m,
            $"expected > 30% saved, measured {result.SavedPercent:0.0}% " +
            $"({result.SharedBytes} B shared vs {result.UnsharedBytes} B unshared)");
    }

    [Fact]
    public void Get_UnknownSymbol_Throws()
    {
        var factory = new InstrumentFactory(InstrumentCatalog.Default());

        Assert.Throws<KeyNotFoundException>(() => factory.Get("NOPE"));
        Assert.Equal(0, factory.Count);
    }
}
