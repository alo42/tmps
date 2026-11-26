using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;

namespace WealthTracker.Patterns.Observer;

/// <summary>
/// OBSERVER - concrete observer: keeps the running total of realised gains,
/// the figure that is taxed. An undone sale is taken back out of the total.
/// </summary>
public sealed class RealisedGainsTracker : ITradeObserver
{
    private readonly TextWriter _output;

    public RealisedGainsTracker(TextWriter output)
    {
        _output = output;
    }

    public decimal Total { get; private set; }

    public void OnTrade(TradeEvent change)
    {
        if (change.Trade.Side != TradeSide.Sell)
            return;
        var gain = change.Kind == TradeEventKind.Executed ? change.Trade.RealisedGain : -change.Trade.RealisedGain;
        Total += gain;
        _output.WriteLine($"  [gains]  {Formats.SignedMoney(gain)} realised, total {Formats.SignedMoney(Total)}");
    }
}
