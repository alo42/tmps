using System.Globalization;
using System.Runtime.CompilerServices;
using WealthTracker.Creational;
using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;
using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Proxy;

namespace WealthTracker.Client;

/// <summary>
/// Interactive mode (<c>dotnet run -- shell</c>): the Flyweight and the Proxy at
/// work while you type. Every purchase shows whether the factory reused an
/// instrument object or created one; every action goes through the proxy of
/// the current user and shows whether it was allowed.
/// </summary>
public sealed class LiveShell
{
    private readonly InstrumentCatalog _catalog;
    private readonly InstrumentFactory _instruments;
    private readonly IPortfolio _portfolio;
    private readonly IQuoteService _quotes = InMemoryQuoteService.Demo();
    private readonly RendererFactory _renderers = RendererFactory.Default();
    private readonly Dictionary<string, (User User, PortfolioAccessProxy Proxy)> _users;
    private readonly TextWriter _output;
    private readonly DateOnly _today;
    private (User User, PortfolioAccessProxy Proxy) _current;

    public LiveShell(TextWriter output, DateOnly today)
    {
        _output = output;
        _today = today;
        _catalog = InstrumentCatalog.Default();
        _instruments = new InstrumentFactory(_catalog);
        _portfolio = new PortfolioDirector(new PortfolioBuilder(_instruments)).BuildDemo();

        // One proxy per user, all in front of the same real portfolio.
        _users = new(StringComparer.OrdinalIgnoreCase);
        foreach (var user in new[] { new User("Adrian", Role.Owner), new User("Ion", Role.Advisor), new User("Visitor", Role.Guest) })
            _users[user.Name] = (user, new PortfolioAccessProxy(_portfolio, user));
        _users["guest"] = _users["Visitor"];
        _current = _users["Adrian"];
    }

    public void Run(TextReader input, bool prompt)
    {
        _output.WriteLine($"Portfolio '{_portfolio.Name}': {_portfolio.Lots.Count} lots, {_instruments.Count} instrument objects. Type 'help'.");
        while (true)
        {
            if (prompt)
                _output.Write($"{_current.User.Name}> ");
            var line = input.ReadLine();
            if (line is null || line.Trim() is "quit" or "exit")
                return;
            Execute(line);
        }
    }

    public void Execute(string line)
    {
        var words = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (words.Length == 0)
            return;
        try
        {
            switch (words[0].ToLowerInvariant())
            {
                case "as": SwitchUser(words); break;
                case "buy": Buy(words[1..]); break;
                case "sell": Sell(words[1..]); break;
                case "lots": Lots(words[1..]); break;
                case "pool": Pool(); break;
                case "report": Report(words[1..]); break;
                case "log": Log(); break;
                case "help": Help(); break;
                default: _output.WriteLine($"  unknown command '{words[0]}' - type 'help'"); break;
            }
        }
        catch (AccessDeniedException ex)
        {
            _output.WriteLine($"  proxy      DENIED   {ex.Message}  (the real portfolio was not touched)");
        }
        catch (Exception ex) when (ex is ArgumentException or FormatException or KeyNotFoundException or IndexOutOfRangeException)
        {
            _output.WriteLine($"  error      {(ex is IndexOutOfRangeException ? "missing argument - type 'help'" : ex.Message)}");
        }
    }

    private void SwitchUser(string[] words)
    {
        if (!_users.TryGetValue(words[1], out var user))
            throw new ArgumentException("Users: adrian (Owner), ion (Advisor), guest (Guest).");
        _current = user;
        _output.WriteLine($"  now acting as {user.User.Name} ({user.User.Role.Name}) - permissions: {user.User.Role.Permissions}");
    }

    /// <summary>buy SYMBOL QTY [PRICE] - Flyweight first (get the instrument), then the Proxy (add the lot).</summary>
    private void Buy(string[] args)
    {
        var (symbol, quantity) = decimal.TryParse(args[0], NumberStyles.Number, CultureInfo.InvariantCulture, out _)
            ? (args[1], args[0]) : (args[0], args[1]);       // "buy 2 VWCE" or "buy VWCE 2"

        var before = _instruments.Count;
        var instrument = _instruments.Get(symbol);           // FLYWEIGHT: reuse or create
        var created = _instruments.Count > before;
        _output.WriteLine($"  flyweight  {instrument.Symbol} -> {(created ? "NEW object" : "existing object")} {Id(instrument)}" +
                          $"{(created ? "  (first request: read from the catalog)" : "  (nothing created)")}" +
                          $"   pool: {_instruments.Count} objects, catalog reads: {_catalog.Lookups}");

        var price = args.Length > 2 ? Number(args[2]) : _quotes.PriceOf(instrument.Symbol);
        var lot = new Lot(instrument, Number(quantity), price, _today);
        _current.Proxy.AddLot(lot);                           // PROXY: checks Trade first
        _output.WriteLine($"  proxy      ALLOWED  {_current.User.Name} bought {Formats.Quantity(lot.Quantity)} {instrument.Symbol} @ {Formats.Money(price)}");
    }

    /// <summary>sell SYMBOL - removes the newest lot of that instrument, through the proxy.</summary>
    private void Sell(string[] args)
    {
        var lot = _current.Proxy.Lots                         // PROXY: View check
            .LastOrDefault(l => string.Equals(l.Instrument.Symbol, args[0], StringComparison.OrdinalIgnoreCase))
            ?? throw new ArgumentException($"No lot of '{args[0]}' to sell.");
        _current.Proxy.RemoveLot(lot);                        // PROXY: Trade check
        _output.WriteLine($"  proxy      ALLOWED  {_current.User.Name} sold the lot of {Formats.Quantity(lot.Quantity)} {lot.Instrument.Symbol} from {lot.Purchased:yyyy-MM-dd}");
    }

    /// <summary>lots SYMBOL - every lot of one instrument and the object it points to.</summary>
    private void Lots(string[] args)
    {
        var lots = _current.Proxy.Lots                        // PROXY: View check
            .Where(l => string.Equals(l.Instrument.Symbol, args[0], StringComparison.OrdinalIgnoreCase))
            .ToList();
        _output.WriteLine($"  proxy      ALLOWED  {_current.User.Name} reads the lots");
        foreach (var lot in lots.Take(5))
            _output.WriteLine($"    {Formats.Quantity(lot.Quantity),8} @ {Formats.Money(lot.UnitCost),10}  {lot.Purchased:yyyy-MM-dd}  -> instrument {Id(lot.Instrument)}");
        if (lots.Count > 5)
            _output.WriteLine($"    ... {lots.Count - 5} more");
        var objects = lots.Select(l => l.Instrument).Distinct().Select(Id).ToList();
        _output.WriteLine($"  flyweight  {lots.Count} lots -> {objects.Count} shared object(s): {string.Join(", ", objects)}");
    }

    /// <summary>pool - what the factory holds: one object per symbol, however many lots use it.</summary>
    private void Pool()
    {
        _output.WriteLine($"  flyweight  pool: {_instruments.Count} objects, catalog reads: {_catalog.Lookups}, lots: {_portfolio.Lots.Count}");
        foreach (var group in _portfolio.Lots.GroupBy(l => l.Instrument).OrderByDescending(g => g.Count()))
            _output.WriteLine($"    {group.Key.Symbol,-9} {Id(group.Key)}  used by {group.Count(),3} lot(s)");
    }

    private void Report(string[] args)
    {
        var renderer = _renderers.Create(args.Length > 0 ? args[0] : "console");
        _output.Write(new HoldingsReport(renderer).Render(_current.Proxy, _quotes));   // reads through the proxy
    }

    private void Log()
    {
        foreach (var e in _current.Proxy.AccessLog)
            _output.WriteLine($"  {(e.Allowed ? "ALLOWED" : "DENIED ")}  {e.User}: {e.Action}");
    }

    private void Help() => _output.WriteLine(
        """
          as adrian|ion|guest        switch user (Owner: view + trade, Advisor: view, Guest: nothing)
          buy SYMBOL QTY [PRICE]     Flyweight: reused or new instrument object; Proxy: allowed or denied
          sell SYMBOL                remove the newest lot of SYMBOL through the proxy
          lots SYMBOL                the lots of SYMBOL and the instrument object each one points to
          pool                       every shared instrument object and how many lots use it
          report [console|markdown|csv]   holdings report read through the current user's proxy
          log                        the current user's access log
          quit
          #ABCD is the object's identity in memory: the same id means the very same object.
          Symbols: AAPL MSFT VWCE BTC ETH EUR-CASH, and NVDA (in the catalog, not yet bought).
        """);

    private static string Id(object o) => $"#{RuntimeHelpers.GetHashCode(o) & 0xFFFF:X4}";

    private static decimal Number(string text) =>
        decimal.TryParse(text, NumberStyles.Number, CultureInfo.InvariantCulture, out var value)
            ? value
            : throw new FormatException($"'{text}' is not a number - e.g. 'buy VWCE 2'.");
}
