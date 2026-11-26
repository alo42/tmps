namespace WealthTracker.Patterns.Observer;

/// <summary>
/// OBSERVER - the subject interface. Observers can be added and removed while
/// the program runs; the subject knows them only through <see cref="ITradeObserver"/>.
/// </summary>
public interface ITradeSubject
{
    void Subscribe(ITradeObserver observer);

    void Unsubscribe(ITradeObserver observer);
}
