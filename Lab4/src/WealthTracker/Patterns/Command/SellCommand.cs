using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;

namespace WealthTracker.Patterns.Command;

/// <summary>
/// COMMAND - concrete command: record a sale. Which lots are sold is decided by
/// the account's current lot-selection strategy when the command first runs.
/// </summary>
public sealed class SellCommand : TradeCommand
{
    private readonly string _symbol;
    private readonly decimal _quantity;
    private readonly decimal _price;
    private readonly DateOnly _date;

    public SellCommand(TradingAccount account, string symbol, decimal quantity, decimal price, DateOnly date)
        : base(account)
    {
        _symbol = symbol.ToUpperInvariant();
        _quantity = quantity;
        _price = price;
        _date = date;
    }

    public override string Description => $"sell {Formats.Quantity(_quantity)} {_symbol} @ {Formats.Money(_price)}";

    protected override TradeReceipt Place() => Account.Sell(_symbol, _quantity, _price, _date);
}
