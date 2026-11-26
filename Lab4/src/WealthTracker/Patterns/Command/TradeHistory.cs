namespace WealthTracker.Patterns.Command;

/// <summary>
/// COMMAND - the invoker. Runs commands and keeps them, so the last one can be
/// undone and an undone one redone. It knows only <see cref="ITradeCommand"/>.
/// </summary>
public sealed class TradeHistory
{
    private readonly Stack<ITradeCommand> _done = new();
    private readonly Stack<ITradeCommand> _undone = new();

    public bool CanUndo => _done.Count > 0;
    public bool CanRedo => _undone.Count > 0;

    /// <summary>The commands in effect, oldest first.</summary>
    public IReadOnlyList<ITradeCommand> Done => _done.Reverse().ToList();

    public void Execute(ITradeCommand command)
    {
        ArgumentNullException.ThrowIfNull(command);
        command.Execute();   // if this throws, nothing is recorded
        _done.Push(command);
        _undone.Clear();     // a new action ends the old redo branch
    }

    public ITradeCommand Undo()
    {
        if (!CanUndo)
            throw new InvalidOperationException("Nothing to undo.");
        var command = _done.Peek();
        command.Undo();      // only moved to the redo stack if the undo succeeded
        _undone.Push(_done.Pop());
        return command;
    }

    public ITradeCommand Redo()
    {
        if (!CanRedo)
            throw new InvalidOperationException("Nothing to redo.");
        var command = _undone.Peek();
        command.Execute();
        _done.Push(_undone.Pop());
        return command;
    }
}
