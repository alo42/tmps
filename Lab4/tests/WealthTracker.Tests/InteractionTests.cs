using WealthTracker.Client;
using WealthTracker.Creational;
using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;
using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Command;
using WealthTracker.Patterns.Observer;
using WealthTracker.Patterns.Proxy;
using WealthTracker.Patterns.Strategy;

namespace WealthTracker.Tests;

/// <summary>Execution paths that cross several patterns, structural (Lab 3) and behavioral (Lab 4).</summary>
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
    public void SellCommand_AsksTheStrategy_ThenAnnouncesTheResult()
    {
        // Command -> receiver -> Strategy picks the lots -> Observers are told.
        var f = new TradingFixture(new HighestCostSelection());
        var gains = new RealisedGainsTracker(TextWriter.Null);
        var log = new ActivityLog(TextWriter.Null);
        f.Account.Subscribe(gains);
        f.Account.Subscribe(log);
        var history = new TradeHistory();

        history.Execute(new SellCommand(f.Account, "ETH", 2m, TradingFixture.EthPrice, TradingFixture.Today));

        Assert.Equal(-1_038.50m, gains.Total);
        Assert.Contains("HIFO: 1.5 from 2024-03-11 @ 3,900.00, 0.5 from 2024-08-05 @ 2,300.00", Assert.Single(log.Entries));
        Assert.True(history.CanUndo);
    }

    [Fact]
    public void AdvisorSellCommand_IsRefusedByTheProxy_NotRecorded_AndNotAnnounced()
    {
        var f = new TradingFixture();
        var advisor = new PortfolioAccessProxy(f.Portfolio, new User("Ion", Role.Advisor));
        var account = new TradingAccount(advisor, f.Instruments, new FifoSelection());
        var log = new ActivityLog(TextWriter.Null);
        account.Subscribe(log);
        var history = new TradeHistory();

        Assert.Throws<AccessDeniedException>(() =>
            history.Execute(new SellCommand(account, "ETH", 1m, TradingFixture.EthPrice, TradingFixture.Today)));

        Assert.False(history.CanUndo);
        Assert.Empty(log.Entries);
        Assert.Equal(4, f.Portfolio.Lots.Count);
    }

    [Fact]
    public void TypedCommands_SwitchTheStrategyAndTheObservers_WhileTheProgramRuns()
    {
        var f = new TradingFixture();
        var output = new StringWriter();
        var log = new ActivityLog(TextWriter.Null);
        var gains = new RealisedGainsTracker(TextWriter.Null);
        var shell = new TradeShell(f.Account, new TradeHistory(), LotSelectionFactory.Default(),
            new Dictionary<string, ITradeObserver> { ["log"] = log, ["gains"] = gains },
            InMemoryQuoteService.Demo(), new HoldingsReport(new ConsoleTableRenderer()), output, TradingFixture.Today);

        shell.Run(new StringReader("""
            watch log
            watch gains
            method hifo
            sell ETH 2
            unwatch log
            undo
            method nonsense
            quit
            sell ETH 1
            """), prompt: false);

        Assert.Equal(0m, gains.Total);                            // the sale and its undo
        Assert.Single(log.Entries);                               // log left before the undo
        Assert.Equal("HIFO", f.Account.LotSelection.Name);       // still HIFO after the bad name
        Assert.Contains("error    Unknown lot-selection method 'nonsense'", output.ToString());
        Assert.Equal(7.7m, f.Account.QuantityHeld("ETH"));        // nothing ran after "quit"
    }

    [Fact]
    public void TypedOrders_AcceptEitherWordOrder_AndExplainMistakes()
    {
        var f = new TradingFixture();
        var output = new StringWriter();
        var shell = new TradeShell(f.Account, new TradeHistory(), LotSelectionFactory.Default(),
            new Dictionary<string, ITradeObserver>(), InMemoryQuoteService.Demo(),
            new HoldingsReport(new ConsoleTableRenderer()), output, TradingFixture.Today);

        shell.Execute("SELL 2 AAPL");          // quantity first, upper-case verb
        shell.Execute("sell AAPL 1");          // symbol first
        shell.Execute("sell AAPL two");
        shell.Execute("buy ETH 1 3000 26.11.2026");

        Assert.Equal(5m, f.Account.QuantityHeld("AAPL"));                         // 8 - 2 - 1
        Assert.Equal(7.7m, f.Account.QuantityHeld("ETH"));                        // the bad buy did nothing
        Assert.Contains("'two' is not a number. Usage: buy|sell SYMBOL QTY", output.ToString());
        Assert.Contains("'26.11.2026' is not a date - write it as YYYY-MM-DD.", output.ToString());
    }

    [Fact]
    public void ConsoleDemo_RunsEverySection()
    {
        var output = new StringWriter();

        var exitCode = ConsoleDemo.Run(output);

        Assert.Equal(0, exitCode);
        var text = output.ToString();
        Assert.Contains("=== 1. Setup", text);
        Assert.Contains("=== 5. All together", text);
        Assert.Contains("[gains]  -1,038.50 realised, total -1,038.50", text);
        Assert.Contains("denied   Ion (Advisor) is not allowed to remove a lot of 4.2 ETH.", text);
        Assert.DoesNotContain("error", text);
    }
}
