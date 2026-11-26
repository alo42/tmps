using WealthTracker.Domain;

namespace WealthTracker.Patterns.Command;

/// <summary>
/// COMMAND - shared base of the concrete commands. It keeps the receiver (the
/// <see cref="TradingAccount"/>) and the receipt of the first run. Undo and redo
/// replay that receipt, so they restore exactly the same lots. The trading rules
/// stay in the receiver; a command only remembers what to call.
/// </summary>
public abstract class TradeCommand : ITradeCommand
{
    private bool _executed;

    protected TradeCommand(TradingAccount account)
    {
        ArgumentNullException.ThrowIfNull(account);
        Account = account;
    }

    /// <summary>The receiver.</summary>
    protected TradingAccount Account { get; }

    /// <summary>What the first run changed; null until then.</summary>
    public TradeReceipt? Receipt { get; private set; }

    public abstract string Description { get; }

    /// <summary>The one step that differs between commands: ask the receiver to trade.</summary>
    protected abstract TradeReceipt Place();

    public void Execute()
    {
        if (_executed)
            throw new InvalidOperationException($"'{Description}' has already been executed.");
        if (Receipt is null)
            Receipt = Place();               // first run: the account applies its rules
        else
            Account.Reapply(Receipt);        // redo: the very same lots again
        _executed = true;
    }

    public void Undo()
    {
        if (!_executed || Receipt is null)
            throw new InvalidOperationException($"'{Description}' has not been executed.");
        Account.Reverse(Receipt);
        _executed = false;
    }
}
