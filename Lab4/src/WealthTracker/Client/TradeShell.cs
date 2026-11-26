using System.Globalization;
using WealthTracker.Creational;
using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;
using WealthTracker.Patterns.Command;
using WealthTracker.Patterns.Observer;
using WealthTracker.Patterns.Proxy;

namespace WealthTracker.Client;

/// <summary>
/// Client code driven by what the user types. Each line changes how the
/// program behaves while it runs: trades become commands in the history,
/// <c>method</c> swaps the lot-selection strategy, <c>watch</c>/<c>unwatch</c>
/// subscribe and unsubscribe observers. The shell works with the pattern
/// interfaces; concrete strategies and observers are looked up by name.
/// </summary>
public sealed class TradeShell
{
    private readonly TradingAccount _account;
    private readonly TradeHistory _history;
    private readonly LotSelectionFactory _methods;
    private readonly IReadOnlyDictionary<string, ITradeObserver> _observers;
    private readonly HashSet<string> _watching = new(StringComparer.OrdinalIgnoreCase);
    private readonly IQuoteService _quotes;
    private readonly Report _holdings;
    private readonly TextWriter _output;
    private readonly DateOnly _today;
    private readonly Dictionary<string, Action<string[]>> _verbs;

    public TradeShell(TradingAccount account, TradeHistory history, LotSelectionFactory methods,
                      IReadOnlyDictionary<string, ITradeObserver> observers, IQuoteService quotes,
                      Report holdings, TextWriter output, DateOnly today)
    {
        _account = account;
        _history = history;
        _methods = methods;
        _observers = observers;
        _quotes = quotes;
        _holdings = holdings;
        _output = output;
        _today = today;
        _verbs = new(StringComparer.OrdinalIgnoreCase)
        {
            ["buy"] = a => _history.Execute(new BuyCommand(_account, Arg(a, 0), Number(Arg(a, 1)), PriceOr(a, 2), DateOr(a, 3))),
            ["sell"] = a => _history.Execute(new SellCommand(_account, Arg(a, 0), Number(Arg(a, 1)), PriceOr(a, 2), DateOr(a, 3))),
            ["undo"] = _ => _history.Undo(),
            ["redo"] = _ => _history.Redo(),
            ["history"] = _ => ShowHistory(),
            ["method"] = Method,
            ["watch"] = a => Watch(a, subscribe: true),
            ["unwatch"] = a => Watch(a, subscribe: false),
            ["holdings"] = _ => _output.Write(_holdings.Render(_account.Portfolio, _quotes)),
            ["help"] = _ => Help(),
        };
    }

    /// <summary>Reads lines until the input ends or the user types "quit".</summary>
    public void Run(TextReader input, bool prompt)
    {
        while (true)
        {
            if (prompt)
                _output.Write("> ");
            var line = input.ReadLine();
            if (line is null || line.Trim() is "quit" or "exit")
                return;
            Execute(line);
        }
    }

    /// <summary>Runs one line. Mistakes are reported, never thrown, so the session goes on.</summary>
    public void Execute(string line)
    {
        var words = line.Split(' ', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        if (words.Length == 0 || words[0].StartsWith('#'))
            return;
        if (!_verbs.TryGetValue(words[0], out var verb))
        {
            _output.WriteLine($"  unknown command '{words[0]}' - type 'help'");
            return;
        }
        try
        {
            verb(words[1..]);
        }
        catch (AccessDeniedException ex)
        {
            _output.WriteLine($"  denied   {ex.Message}");
        }
        catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or FormatException
                                       or KeyNotFoundException)
        {
            _output.WriteLine($"  error    {ex.Message}");
        }
    }

    private void Method(string[] args)
    {
        if (args.Length > 0)
            _account.UseLotSelection(_methods.Create(args[0]));
        _output.WriteLine($"  lot selection: {_account.LotSelection.Name}   (known: {string.Join(", ", _methods.KnownMethods)})");
    }

    private void Watch(string[] args, bool subscribe)
    {
        if (args.Length > 0)
        {
            if (!_observers.TryGetValue(args[0], out var observer))
                throw new ArgumentException($"Unknown observer '{args[0]}'. Known: {string.Join(", ", _observers.Keys)}.");
            if (subscribe)
            {
                _account.Subscribe(observer);
                _watching.Add(args[0]);
            }
            else
            {
                _account.Unsubscribe(observer);
                _watching.Remove(args[0]);
            }
        }
        var watching = _observers.Keys.Where(_watching.Contains).ToList();
        _output.WriteLine($"  watching: {(watching.Count == 0 ? "nothing" : string.Join(", ", watching))}");
    }

    private void ShowHistory()
    {
        var done = _history.Done;
        if (done.Count == 0)
            _output.WriteLine("  history is empty");
        for (var i = 0; i < done.Count; i++)
            _output.WriteLine($"  {i + 1}. {done[i].Description}");
    }

    private void Help() => _output.WriteLine(
        """
          buy  SYMBOL QTY [PRICE] [YYYY-MM-DD]   record a purchase (price defaults to the current quote)
          sell SYMBOL QTY [PRICE] [YYYY-MM-DD]   record a sale; the lot-selection method picks the lots
          undo | redo | history                  step back, step forward, list the trades in effect
          method [fifo|lifo|hifo]                show or switch the lot-selection method
          watch | unwatch [log|gains|alerts]     subscribe or unsubscribe an observer
          holdings                               holdings report
          quit
        """);

    private decimal PriceOr(string[] args, int index) =>
        args.Length > index ? Number(args[index]) : _quotes.PriceOf(args[0]);

    private DateOnly DateOr(string[] args, int index) =>
        args.Length > index ? DateOnly.ParseExact(args[index], "yyyy-MM-dd", CultureInfo.InvariantCulture) : _today;

    private static string Arg(string[] args, int index) =>
        args.Length > index ? args[index] : throw new ArgumentException("Missing argument - type 'help'.");

    private static decimal Number(string text) => decimal.Parse(text, NumberStyles.Number, CultureInfo.InvariantCulture);
}
