using WealthTracker.Creational;
using WealthTracker.Patterns.Bridge;
using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Tests;

/// <summary>The creational patterns reused from Lab 2 to create the structural patterns' objects.</summary>
public class CreationalTests
{
    [Fact]
    public void Builder_TakesInstrumentsFromTheFlyweightFactory()
    {
        var instruments = new InstrumentFactory(InstrumentCatalog.Default());
        var builder = new PortfolioBuilder(instruments);
        var day = new DateOnly(2025, 1, 2);

        var mine = builder.Named("Mine").Buy("BTC", 0.1m, 60_000m, day).Build();
        var yours = builder.Named("Yours").Buy("BTC", 0.2m, 61_000m, day).Build();

        Assert.Same(mine.Lots[0].Instrument, yours.Lots[0].Instrument);
    }

    [Fact]
    public void Builder_RejectsAnEmptyPortfolio()
    {
        var builder = new PortfolioBuilder(new InstrumentFactory(InstrumentCatalog.Default()));

        Assert.Throws<InvalidOperationException>(() => builder.Build());
    }

    [Fact]
    public void RendererFactory_CreatesTheRendererForEachFormat()
    {
        var factory = RendererFactory.Default();

        Assert.IsType<ConsoleTableRenderer>(factory.Create("console"));
        Assert.IsType<MarkdownRenderer>(factory.Create("MARKDOWN"));
        Assert.IsType<CsvRenderer>(factory.Create("csv"));
    }

    [Fact]
    public void RendererFactory_NewFormat_IsRegisteredWithoutEditingTheFactory()
    {
        var factory = RendererFactory.Default().Register("md", () => new MarkdownRenderer());

        Assert.IsType<MarkdownRenderer>(factory.Create("md"));
        var error = Assert.Throws<ArgumentException>(() => factory.Create("pdf"));
        Assert.Contains("console, csv, markdown, md", error.Message);
    }
}
