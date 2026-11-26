using WealthTracker.Domain;
using WealthTracker.Patterns.Command;
using WealthTracker.Patterns.Observer;

namespace WealthTracker.Tests;

public class ObserverTests
{
    /// <summary>Records every event it receives.</summary>
    private sealed class SpyObserver : ITradeObserver
    {
        public List<TradeEvent> Received { get; } = [];
        public void OnTrade(TradeEvent change) => Received.Add(change);
    }

    [Fact]
    public void EverySubscribedObserver_IsNotified()
    {
        var f = new TradingFixture();
        var first = new SpyObserver();
        var second = new SpyObserver();
        f.Account.Subscribe(first);
        f.Account.Subscribe(second);

        f.Account.Buy("AAPL", 1m, 200m, TradingFixture.Today);

        Assert.Single(first.Received);
        var change = Assert.Single(second.Received);
        Assert.Equal((TradeEventKind.Executed, TradeSide.Buy, "AAPL"),
                     (change.Kind, change.Trade.Side, change.Trade.Instrument.Symbol));
        Assert.Equal(5, change.Lots.Count);   // observers see the portfolio after the change
    }

    [Fact]
    public void UnsubscribedObserver_IsNotNotified_TheOthersStillAre()
    {
        var f = new TradingFixture();
        var stays = new SpyObserver();
        var leaves = new SpyObserver();
        f.Account.Subscribe(stays);
        f.Account.Subscribe(leaves);
        f.Account.Buy("AAPL", 1m, 200m, TradingFixture.Today);

        f.Account.Unsubscribe(leaves);                          // at runtime
        f.Account.Sell("AAPL", 1m, 214.50m, TradingFixture.Today);

        Assert.Equal(2, stays.Received.Count);
        Assert.Single(leaves.Received);
    }

    [Fact]
    public void SubscribingTwice_StillNotifiesOnce()
    {
        var f = new TradingFixture();
        var spy = new SpyObserver();
        f.Account.Subscribe(spy);
        f.Account.Subscribe(spy);

        f.Account.Buy("AAPL", 1m, 200m, TradingFixture.Today);

        Assert.Single(spy.Received);
    }

    [Fact]
    public void UndoIsAnnounced_SoRealisedGainsGoBackToZero()
    {
        var f = new TradingFixture();
        var gains = new RealisedGainsTracker(TextWriter.Null);
        f.Account.Subscribe(gains);
        var history = new TradeHistory();

        history.Execute(new SellCommand(f.Account, "ETH", 2m, TradingFixture.EthPrice, TradingFixture.Today));
        Assert.Equal(2_261.50m, gains.Total);                   // FIFO
        history.Undo();

        Assert.Equal(0m, gains.Total);
    }

    [Fact]
    public void ConcentrationAlert_FiresOnlyAboveTheLimit()
    {
        var f = new TradingFixture();
        var alert = new ConcentrationAlert(InMemoryQuoteService.Demo(), limitPercent: 50m, TextWriter.Null);
        f.Account.Subscribe(alert);

        f.Account.Buy("AAPL", 1m, 214.50m, TradingFixture.Today);  // AAPL ~7.8% of the value
        Assert.Empty(alert.Alerts);
        f.Account.Buy("ETH", 0.1m, 2_980.75m, TradingFixture.Today); // ETH ~92%

        Assert.StartsWith("ETH is 92.", Assert.Single(alert.Alerts));
    }

    [Fact]
    public void ActivityLog_ShowsTheLotsTheStrategyChose()
    {
        var f = new TradingFixture();
        var log = new ActivityLog(TextWriter.Null);
        f.Account.Subscribe(log);
        var history = new TradeHistory();

        history.Execute(new SellCommand(f.Account, "ETH", 2m, TradingFixture.EthPrice, TradingFixture.Today));
        history.Undo();

        Assert.Equal(
        [
            "SELL 2 ETH @ 2,980.75 on 2026-11-26 - FIFO: 2 from 2023-03-12 @ 1,850.00",
            "UNDONE SELL 2 ETH @ 2,980.75 on 2026-11-26 - FIFO: 2 from 2023-03-12 @ 1,850.00",
        ], log.Entries);
    }

    /// <summary>A badly behaved observer that trades whenever it hears about a trade.</summary>
    private sealed class EchoTrader(TradingAccount account) : ITradeObserver
    {
        public int Calls { get; private set; }
        public void OnTrade(TradeEvent change)
        {
            Calls++;
            account.Buy("AAPL", 1m, 200m, TradingFixture.Today);
        }
    }

    [Fact]
    public void ObserverThatTrades_IsStopped_InsteadOfLoopingForever()
    {
        var f = new TradingFixture();
        var echo = new EchoTrader(f.Account);
        f.Account.Subscribe(echo);

        Assert.Throws<InvalidOperationException>(() => f.Account.Buy("ETH", 1m, 3_000m, TradingFixture.Today));
        Assert.Equal(1, echo.Calls);
    }
}
