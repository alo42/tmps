using WealthTracker.Domain;
using WealthTracker.Patterns.Command;
using WealthTracker.Patterns.Strategy;

namespace WealthTracker.Tests;

public class CommandTests
{
    private static void AssertSameLots(IEnumerable<Lot> expected, IEnumerable<Lot> actual) =>
        Assert.True(new HashSet<Lot>(expected).SetEquals(actual) && expected.Count() == actual.Count(),
                    "The portfolio does not hold exactly the expected lot objects.");

    [Fact]
    public void BuyThenUndo_RestoresTheOriginalLots()
    {
        var f = new TradingFixture();
        var before = f.Portfolio.Lots.ToList();
        var history = new TradeHistory();

        history.Execute(new BuyCommand(f.Account, "ETH", 1m, 3_000m, TradingFixture.Today));
        Assert.Equal(5, f.Portfolio.Lots.Count);
        history.Undo();

        AssertSameLots(before, f.Portfolio.Lots);
    }

    [Fact]
    public void SellThenUndo_PutsBackEveryLot_AndDropsTheSplitRest()
    {
        var f = new TradingFixture(new FifoSelection());
        var before = f.Portfolio.Lots.ToList();
        var history = new TradeHistory();

        history.Execute(new SellCommand(f.Account, "ETH", 5m, TradingFixture.EthPrice, TradingFixture.Today));
        Assert.Equal(2.7m, f.Account.QuantityHeld("ETH"));     // 4.2 and 0.8 of 1.5 sold
        history.Undo();

        AssertSameLots(before, f.Portfolio.Lots);
        Assert.Equal(7.7m, f.Account.QuantityHeld("ETH"));
    }

    [Fact]
    public void Redo_ReappliesTheSameLots_EvenIfTheMethodChangedInBetween()
    {
        var f = new TradingFixture(new FifoSelection());
        var history = new TradeHistory();
        var sell = new SellCommand(f.Account, "ETH", 2m, TradingFixture.EthPrice, TradingFixture.Today);
        history.Execute(sell);
        var afterFirstRun = f.Portfolio.Lots.ToList();

        history.Undo();
        f.Account.UseLotSelection(new LifoSelection());
        history.Redo();

        AssertSameLots(afterFirstRun, f.Portfolio.Lots);        // still the FIFO lots
        Assert.Equal("FIFO", sell.Receipt!.Trade.Method);
    }

    [Fact]
    public void NewCommandAfterUndo_ClearsTheRedoStack()
    {
        var f = new TradingFixture();
        var history = new TradeHistory();
        history.Execute(new BuyCommand(f.Account, "AAPL", 1m, 200m, TradingFixture.Today));
        history.Undo();

        history.Execute(new BuyCommand(f.Account, "MSFT", 1m, 400m, TradingFixture.Today));

        Assert.False(history.CanRedo);
        Assert.Equal(["buy 1 MSFT @ 400.00"], history.Done.Select(c => c.Description));
    }

    [Fact]
    public void FailedCommand_IsNotRecorded_AndChangesNothing()
    {
        var f = new TradingFixture();
        var before = f.Portfolio.Lots.ToList();
        var history = new TradeHistory();

        Assert.Throws<InvalidOperationException>(() =>
            history.Execute(new SellCommand(f.Account, "ETH", 100m, TradingFixture.EthPrice, TradingFixture.Today)));

        Assert.False(history.CanUndo);
        Assert.Equal(before, f.Portfolio.Lots);
    }

    [Fact]
    public void Undo_WithNothingDone_Throws()
    {
        var history = new TradeHistory();

        Assert.Throws<InvalidOperationException>(() => history.Undo());
        Assert.Throws<InvalidOperationException>(() => history.Redo());
    }

    /// <summary>A command the project does not have: proves the history depends only on the interface.</summary>
    private sealed class CountingCommand : ITradeCommand
    {
        public int Runs { get; private set; }
        public string Description => "count";
        public void Execute() => Runs++;
        public void Undo() => Runs--;
    }

    [Fact]
    public void History_RunsAnyITradeCommand()
    {
        var history = new TradeHistory();
        var command = new CountingCommand();

        history.Execute(command);
        history.Undo();
        history.Redo();

        Assert.Equal(1, command.Runs);
        Assert.Same(command, Assert.Single(history.Done));
    }
}
