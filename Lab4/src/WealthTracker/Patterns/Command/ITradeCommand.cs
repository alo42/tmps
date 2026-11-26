namespace WealthTracker.Patterns.Command;

/// <summary>
/// COMMAND - the command interface. A trade request turned into an object, so
/// the history can run it, keep it, undo it and run it again.
/// </summary>
public interface ITradeCommand
{
    /// <summary>What the command does, in the words the user typed.</summary>
    string Description { get; }

    void Execute();

    void Undo();
}
