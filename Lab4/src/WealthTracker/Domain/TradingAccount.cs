using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Strategy;

namespace WealthTracker.Domain;

/// <summary>
/// The account a user trades through. It owns the trading rules and works on
/// any <see cref="IPortfolio"/> - including an access proxy.
/// STRATEGY - context: a sale asks the current <see cref="ILotSelectionStrategy"/>
/// which lots to use, and the method can be switched while the program runs.
/// </summary>
public sealed class TradingAccount
{
    private readonly IPortfolio _portfolio;
    private readonly InstrumentFactory _instruments;
    private ILotSelectionStrategy _lotSelection;

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

    public decimal QuantityHeld(string symbol) => LotsOf(symbol).Sum(lot => lot.Quantity);

    public TradeReceipt Buy(string symbol, decimal quantity, decimal price, DateOnly date)
    {
        var lot = new Lot(_instruments.Get(symbol), quantity, price, date); // validates quantity and price
        _portfolio.AddLot(lot);
        return new TradeReceipt(new Trade(TradeSide.Buy, lot.Instrument, quantity, price, date), [lot], []);
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
            throw new InvalidOperationException($"Cannot sell {quantity} {symbol.ToUpperInvariant()}: only {held} held.");

        // The strategy decides which lots; the account carries the sale out.
        var picks = _lotSelection.Select(lots, quantity);
        if (picks.Sum(p => p.Quantity) != quantity || picks.Any(p => !lots.Contains(p.Lot)))
            throw new InvalidOperationException($"{_lotSelection.Name} did not pick {quantity} units from the held lots.");

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
        return new TradeReceipt(trade, added, removed);
    }

    private List<Lot> LotsOf(string symbol) =>
        _portfolio.Lots.Where(lot => string.Equals(lot.Instrument.Symbol, symbol, StringComparison.OrdinalIgnoreCase))
                       .ToList();

    private void Apply(IEnumerable<Lot> remove, IEnumerable<Lot> add)
    {
        foreach (var lot in remove)
            _portfolio.RemoveLot(lot);
        foreach (var lot in add)
            _portfolio.AddLot(lot);
    }
}
