using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Observer;
using WealthTracker.Patterns.Strategy;

namespace WealthTracker.Domain;

/// <summary>
/// The account a user trades through. It owns the trading rules and works on
/// any <see cref="IPortfolio"/> - including an access proxy.
/// <list type="bullet">
/// <item>STRATEGY - context: a sale asks the current <see cref="ILotSelectionStrategy"/>
/// which lots to use, and the method can be switched while the program runs.</item>
/// <item>COMMAND - receiver: trade commands call Buy, Sell, Reverse and Reapply.</item>
/// <item>OBSERVER - subject: every change is announced to the subscribed observers.</item>
/// </list>
/// </summary>
public sealed class TradingAccount : ITradeSubject
{
    private readonly IPortfolio _portfolio;
    private readonly InstrumentFactory _instruments;
    private readonly List<ITradeObserver> _observers = [];
    private ILotSelectionStrategy _lotSelection;
    private bool _notifying;

    public TradingAccount(IPortfolio portfolio, InstrumentFactory instruments, ILotSelectionStrategy lotSelection)
    {
        ArgumentNullException.ThrowIfNull(portfolio);
        ArgumentNullException.ThrowIfNull(instruments);
        ArgumentNullException.ThrowIfNull(lotSelection);
        _portfolio = portfolio;
        _instruments = instruments;
        _lotSelection = lotSelection;
    }

    public IPortfolio Portfolio => _portfolio;

    public ILotSelectionStrategy LotSelection => _lotSelection;

    /// <summary>Swaps the strategy; the next sale uses the new method.</summary>
    public void UseLotSelection(ILotSelectionStrategy lotSelection)
    {
        ArgumentNullException.ThrowIfNull(lotSelection);
        _lotSelection = lotSelection;
    }

    public void Subscribe(ITradeObserver observer)
    {
        ArgumentNullException.ThrowIfNull(observer);
        if (!_observers.Contains(observer))   // subscribing twice must not notify twice
            _observers.Add(observer);
    }

    public void Unsubscribe(ITradeObserver observer) => _observers.Remove(observer);

    public decimal QuantityHeld(string symbol) => LotsOf(symbol).Sum(lot => lot.Quantity);

    public TradeReceipt Buy(string symbol, decimal quantity, decimal price, DateOnly date)
    {
        var lot = new Lot(_instruments.Get(symbol), quantity, price, date); // validates quantity and price
        Apply(remove: [], add: [lot]);
        var receipt = new TradeReceipt(new Trade(TradeSide.Buy, lot.Instrument, quantity, price, date), [lot], []);
        Notify(TradeEventKind.Executed, receipt.Trade);
        return receipt;
    }

    public TradeReceipt Sell(string symbol, decimal quantity, decimal price, DateOnly date)
    {
        if (quantity <= 0)
            throw new ArgumentOutOfRangeException(nameof(quantity), "Quantity must be positive.");
        if (price < 0)
            throw new ArgumentOutOfRangeException(nameof(price), "Price cannot be negative.");
        var lots = LotsOf(symbol);
        var held = lots.Sum(lot => lot.Quantity);
        if (quantity > held)
            throw new InvalidOperationException(FormattableString.Invariant($"Cannot sell {quantity} {symbol.ToUpperInvariant()}: only {held} held."));

        // The strategy decides which lots; the account carries the sale out.
        var picks = _lotSelection.Select(lots, quantity);
        if (picks.Sum(p => p.Quantity) != quantity || picks.Any(p => !lots.Contains(p.Lot)))
            throw new InvalidOperationException(FormattableString.Invariant($"{_lotSelection.Name} did not pick {quantity} units from the held lots."));

        var removed = picks.Select(p => p.Lot).ToList();
        var added = picks.Where(p => p.Quantity < p.Lot.Quantity)   // the unsold rest of a split lot
                         .Select(p => new Lot(p.Lot.Instrument, p.Lot.Quantity - p.Quantity, p.Lot.UnitCost, p.Lot.Purchased))
                         .ToList();
        Apply(remove: removed, add: added);

        var trade = new Trade(TradeSide.Sell, lots[0].Instrument, quantity, price, date)
        {
            Picks = picks,
            Method = _lotSelection.Name,
        };
        Notify(TradeEventKind.Executed, trade);
        return new TradeReceipt(trade, added, removed);
    }

    /// <summary>Undoes a trade: removes the lots it added and puts back the lots it removed.</summary>
    public void Reverse(TradeReceipt receipt)
    {
        ArgumentNullException.ThrowIfNull(receipt);
        Apply(remove: receipt.Added, add: receipt.Removed);
        Notify(TradeEventKind.Reversed, receipt.Trade);
    }

    /// <summary>Repeats a reversed trade with exactly the same lots.</summary>
    public void Reapply(TradeReceipt receipt)
    {
        ArgumentNullException.ThrowIfNull(receipt);
        Apply(remove: receipt.Removed, add: receipt.Added);
        Notify(TradeEventKind.Executed, receipt.Trade);
    }

    private List<Lot> LotsOf(string symbol) =>
        _portfolio.Lots.Where(lot => string.Equals(lot.Instrument.Symbol, symbol, StringComparison.OrdinalIgnoreCase))
                       .ToList();

    private void Apply(IReadOnlyList<Lot> remove, IReadOnlyList<Lot> add)
    {
        if (_notifying)   // an observer that trades would start an endless chain of notifications
            throw new InvalidOperationException("Observers may not trade while they are being notified.");
        if (remove.Any(lot => !_portfolio.Lots.Contains(lot)))
            throw new InvalidOperationException("The portfolio no longer holds the lots this trade expects.");
        foreach (var lot in remove)
            _portfolio.RemoveLot(lot);
        foreach (var lot in add)
            _portfolio.AddLot(lot);
    }

    private void Notify(TradeEventKind kind, Trade trade)
    {
        var change = new TradeEvent(kind, trade, _portfolio.Lots);
        _notifying = true;
        try
        {
            // A copy, so an observer may unsubscribe while it is being notified.
            foreach (var observer in _observers.ToArray())
                observer.OnTrade(change);
        }
        finally
        {
            _notifying = false;
        }
    }
}
