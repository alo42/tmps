namespace WealthTracker.Patterns.Observer;

/// <summary>OBSERVER - the observer interface: told about every trade and every undo.</summary>
public interface ITradeObserver
{
    void OnTrade(TradeEvent change);
}
