using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;

namespace WealthTracker.Patterns.Command;

/// <summary>COMMAND - concrete command: record a purchase.</summary>
public sealed class BuyCommand : TradeCommand
{
    private readonly string _symbol;
    private readonly decimal _quantity;
    private readonly decimal _price;
    private readonly DateOnly _date;

    public BuyCommand(TradingAccount account, string symbol, decimal quantity, decimal price, DateOnly date)
        : base(account)
    {
        _symbol = symbol.ToUpperInvariant();
        _quantity = quantity;
        _price = price;
        _date = date;
    }

    public override string Description => $"buy {Formats.Quantity(_quantity)} {_symbol} @ {Formats.Money(_price)}";

    protected override TradeReceipt Place() => Account.Buy(_symbol, _quantity, _price, _date);
}
