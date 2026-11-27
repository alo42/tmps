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
    public void LiveShell_ShowsSharingAndAccessDecisions_AsTheUserTypes()
    {
        var output = new StringWriter();
        var shell = new LiveShell(output, new DateOnly(2026, 11, 27));

        shell.Run(new StringReader("""
            buy NVDA 3
            buy 0.5 NVDA
            as ion
            buy NVDA 1
            as guest
            lots NVDA
            quit
            """), prompt: false);

        var text = output.ToString();
        Assert.Single(System.Text.RegularExpressions.Regex.Matches(text, "NVDA -> NEW object"));  // created once...
        Assert.Equal(2, System.Text.RegularExpressions.Regex.Matches(text, "NVDA -> existing object").Count); // ...then reused
        Assert.Contains("ALLOWED  Adrian bought 0.5 NVDA", text);
        Assert.Contains("DENIED   Ion (Advisor) is not allowed to buy 1 NVDA.", text);
        Assert.Contains("DENIED   Visitor (Guest) is not allowed to view the lots.", text);
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
