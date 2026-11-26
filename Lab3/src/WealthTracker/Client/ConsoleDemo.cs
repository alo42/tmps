using System.Globalization;
using WealthTracker.Creational;
using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;
using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Proxy;

namespace WealthTracker.Client;

/// <summary>
/// The client. It depends on abstractions - IPortfolio, Report,
/// IReportRenderer, IQuoteService - and creates concrete objects only through
/// the builder and the factories.
/// </summary>
public static class ConsoleDemo
{
    public static int Run(string format, TextWriter output)
    {
        IQuoteService quotes = InMemoryQuoteService.Demo();
        var instruments = new InstrumentFactory(InstrumentCatalog.Default());
        var renderers = RendererFactory.Default();

        // 1. Creational reuse: the director and builder create the portfolio.
        Section(output, "1. Builder + Flyweight factory: building the portfolio");
        IPortfolio portfolio = new PortfolioDirector(new PortfolioBuilder(instruments)).BuildDemo();
        output.WriteLine($"Built '{portfolio.Name}' with {portfolio.Lots.Count} purchase lots.");

        // 2. Flyweight: 43 lots, 6 instrument objects.
        Section(output, "2. Flyweight: lots share instrument data");
        output.WriteLine($"Lots: {portfolio.Lots.Count}    distinct instrument objects: {instruments.Count}");
        var vwce = portfolio.Lots.Where(l => l.Instrument.Symbol == "VWCE").ToList();
        output.WriteLine($"VWCE lots: {vwce.Count}, all pointing at the same object: " +
                         $"{vwce.All(l => ReferenceEquals(l.Instrument, vwce[0].Instrument))}");
        var m = FlyweightMeasurement.Run(100_000);
        output.WriteLine(string.Create(CultureInfo.InvariantCulture,
            $"Allocating {m.Lots:N0} lots: shared {m.SharedBytes:N0} B vs unshared {m.UnsharedBytes:N0} B " +
            $"-> {m.SavedBytes:N0} B saved ({m.SavedPercent:0.0}%)"));

        // 3. Proxy: the advisor may look but not trade.
        Section(output, "3. Proxy: sharing the portfolio with an advisor");
        var owner = new PortfolioAccessProxy(portfolio, new User("Adrian", Role.Owner));
        var advisor = new PortfolioAccessProxy(portfolio, new User("Ion", Role.Advisor));
        var guest = new PortfolioAccessProxy(portfolio, new User("Visitor", Role.Guest));
        var newLot = new Lot(instruments.Get("MSFT"), 1m, 430m, new DateOnly(2025, 11, 3));
        Attempt(output, "Adrian (Owner) buys 1 MSFT", () => owner.AddLot(newLot));
        Attempt(output, "Ion (Advisor) reads the lots", () => _ = advisor.Lots);
        Attempt(output, "Ion (Advisor) sells 1 MSFT", () => advisor.RemoveLot(newLot));
        Attempt(output, "Visitor (Guest) reads the lots", () => _ = guest.Lots);
        owner.RemoveLot(newLot); // restore the demo portfolio

        // 4. Bridge: three reports, each in a different format.
        Section(output, "4. Bridge: reports x formats");
        output.WriteLine("AllocationReport + ConsoleTableRenderer:");
        output.WriteLine(new AllocationReport(renderers.Create("console")).Render(portfolio, quotes));
        output.WriteLine("PerformanceReport + CsvRenderer:");
        output.WriteLine(new PerformanceReport(renderers.Create("csv")).Render(portfolio, quotes));

        // 5. One execution path through all three patterns:
        //    advisor -> Proxy -> Bridge (report + renderer) -> Flyweight instruments.
        Section(output, $"5. All together: the advisor's holdings report ({format})");
        Report report = new HoldingsReport(renderers.Create(format));
        output.WriteLine(report.Render(advisor, quotes));
        output.WriteLine("Advisor access log:");
        foreach (var e in advisor.AccessLog)
            output.WriteLine($"  {(e.Allowed ? "ALLOWED" : "DENIED ")}  {e.User}: {e.Action}");
        return 0;
    }

    private static void Section(TextWriter output, string title)
    {
        output.WriteLine();
        output.WriteLine($"=== {title} ===");
    }

    private static void Attempt(TextWriter output, string description, Action action)
    {
        try
        {
            action();
            output.WriteLine($"  ALLOWED  {description}");
        }
        catch (AccessDeniedException ex)
        {
            output.WriteLine($"  DENIED   {description} - {ex.Message}");
        }
    }
}
