using WealthTracker.Creational;
using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;
using WealthTracker.Patterns.Command;
using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Observer;
using WealthTracker.Patterns.Proxy;

namespace WealthTracker.Client;

/// <summary>
/// Wires the application together and runs it, either as a scripted demo or
/// as an interactive session. Everything behavioral is driven through
/// <see cref="TradeShell"/>, exactly as a user at the keyboard would drive it.
/// </summary>
public static class ConsoleDemo
{
    /// <summary>The date the scripted demo pretends it is, so its output never changes.</summary>
    public static readonly DateOnly DemoDate = new(2026, 11, 26);

    private sealed record Session(IPortfolio Portfolio, InstrumentFactory Instruments, IQuoteService Quotes,
                                  LotSelectionFactory Methods, TradeShell Shell);

    /// <summary>Creates the portfolio (Builder + Flyweight), the owner's proxy and the account.</summary>
    private static Session Open(TextWriter output, DateOnly today)
    {
        IQuoteService quotes = InMemoryQuoteService.Demo();
        var instruments = new InstrumentFactory(InstrumentCatalog.Default());
        var portfolio = new PortfolioDirector(new PortfolioBuilder(instruments)).BuildDemo();
        var methods = LotSelectionFactory.Default();

        IPortfolio owner = new PortfolioAccessProxy(portfolio, new User("Adrian", Role.Owner));
        var account = new TradingAccount(owner, instruments, methods.Create("fifo"));
        var observers = new Dictionary<string, ITradeObserver>(StringComparer.OrdinalIgnoreCase)
        {
            ["log"] = new ActivityLog(output),
            ["gains"] = new RealisedGainsTracker(output),
            ["alerts"] = new ConcentrationAlert(quotes, limitPercent: 35m, output),
        };
        var holdings = new HoldingsReport(RendererFactory.Default().Create("console"));
        var shell = new TradeShell(account, new TradeHistory(), methods, observers, quotes, holdings, output, today);
        return new Session(portfolio, instruments, quotes, methods, shell);
    }

    /// <summary>The scripted walk-through: each section is a few typed commands.</summary>
    public static int Run(TextWriter output)
    {
        var session = Open(output, DemoDate);

        Section(output, "1. Setup: Builder + Flyweight + Proxy from Lab 3");
        output.WriteLine($"Built '{session.Portfolio.Name}' with {session.Portfolio.Lots.Count} lots sharing " +
                         $"{session.Instruments.Count} instrument objects; Adrian (Owner) trades through a PortfolioAccessProxy.");
        Type(session.Shell, output, "watch log", "watch gains", "watch alerts", "method");

        Section(output, "2. Command: trades are objects that can be undone and redone");
        Type(session.Shell, output,
             "buy ETH 1.5 3900 2024-03-11",
             "buy ETH 2 2300 2024-08-05",
             "undo",
             "redo",
             "history");

        Section(output, "3. Strategy: the same sale under FIFO, LIFO and HIFO");
        Type(session.Shell, output,
             "sell ETH 2",
             "undo",
             "method lifo",
             "sell ETH 2",
             "undo",
             "method hifo",
             "sell ETH 2");

        Section(output, "4. Observer: subscribing and unsubscribing at runtime");
        Type(session.Shell, output,
             "unwatch log",
             "sell AAPL 2",
             "watch log",
             "buy VWCE 2",
             "history");

        Section(output, "5. All together: the advisor's sale goes Command -> Strategy -> Proxy and is refused");
        var advisorOutput = new ActivityLog(output);
        var advisorAccount = new TradingAccount(
            new PortfolioAccessProxy(session.Portfolio, new User("Ion", Role.Advisor)),
            session.Instruments, session.Methods.Create("fifo"));
        advisorAccount.Subscribe(advisorOutput);
        var advisorShell = new TradeShell(advisorAccount, new TradeHistory(), session.Methods,
                                          new Dictionary<string, ITradeObserver>(), session.Quotes,
                                          new HoldingsReport(new ConsoleTableRenderer()), output, DemoDate);
        Type(advisorShell, output, "sell ETH 1", "history");
        output.WriteLine($"Observers told about the refused sale: {advisorOutput.Entries.Count}");
        output.WriteLine();
        output.WriteLine("Adrian's holdings after the session (Bridge: HoldingsReport + ConsoleTableRenderer):");
        Type(session.Shell, output, "holdings");
        return 0;
    }

    /// <summary>Lets the user type the commands: dotnet run -- shell</summary>
    public static int Interactive(TextReader input, TextWriter output, DateOnly today)
    {
        var session = Open(output, today);
        output.WriteLine($"Wealth tracker - '{session.Portfolio.Name}', {session.Portfolio.Lots.Count} lots. Type 'help', or 'quit' to leave.");
        foreach (var line in new[] { "watch log", "watch gains", "watch alerts", "method" })
            session.Shell.Execute(line);
        session.Shell.Run(input, prompt: true);
        return 0;
    }

    private static void Type(TradeShell shell, TextWriter output, params string[] lines)
    {
        foreach (var line in lines)
        {
            output.WriteLine($"> {line}");
            shell.Execute(line);
        }
    }

    private static void Section(TextWriter output, string title)
    {
        output.WriteLine();
        output.WriteLine($"=== {title} ===");
    }
}
