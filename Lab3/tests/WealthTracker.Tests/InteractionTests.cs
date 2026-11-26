using WealthTracker.Client;
using WealthTracker.Creational;
using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;
using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Proxy;

namespace WealthTracker.Tests;

/// <summary>One execution path through all three patterns: Proxy -> Bridge -> Flyweight.</summary>
public class InteractionTests
{
    private static readonly IQuoteService Quotes = InMemoryQuoteService.Demo();

    [Fact]
    public void AdvisorReport_GoesThroughProxy_Bridge_AndSharedInstruments()
    {
        var instruments = new InstrumentFactory(InstrumentCatalog.Default());
        var portfolio = new PortfolioDirector(new PortfolioBuilder(instruments)).BuildDemo();
        var advisor = new PortfolioAccessProxy(portfolio, new User("Ion", Role.Advisor));

        Report report = new HoldingsReport(RendererFactory.Default().Create("markdown"));
        var markdown = report.Render(advisor, Quotes);

        Assert.Contains(TestData.TotalValue, markdown);           // Bridge produced the report
        Assert.All(advisor.AccessLog, e => Assert.True(e.Allowed)); // Proxy allowed the reads
        Assert.Equal(43, portfolio.Lots.Count);                    // 43 lots...
        Assert.Equal(6, instruments.Count);                        // ...6 shared flyweights
    }

    [Fact]
    public void Advisor_CannotTrade_OnTheSamePath()
    {
        var instruments = new InstrumentFactory(InstrumentCatalog.Default());
        var portfolio = new PortfolioDirector(new PortfolioBuilder(instruments)).BuildDemo();
        IPortfolio advisor = new PortfolioAccessProxy(portfolio, new User("Ion", Role.Advisor));

        Assert.Throws<AccessDeniedException>(() => advisor.RemoveLot(advisor.Lots[0]));
        Assert.Equal(43, portfolio.Lots.Count);
    }

    [Fact]
    public void ConsoleDemo_RunsEverySection()
    {
        var output = new StringWriter();

        var exitCode = ConsoleDemo.Run("markdown", output);

        Assert.Equal(0, exitCode);
        var text = output.ToString();
        Assert.Contains("=== 1. Builder", text);
        Assert.Contains("=== 5. All together", text);
        Assert.Contains("DENIED   Ion (Advisor) sells 1 MSFT", text);
        Assert.Contains($"**Total value:** {TestData.TotalValue}", text);
    }
}
