using WealthTracker.Domain;
using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Proxy;

namespace WealthTracker.Tests;

public class ProxyTests
{
    private static readonly InstrumentFactory Instruments = new(InstrumentCatalog.Default());

    private static Lot AppleLot() => new(Instruments.Get("AAPL"), 3m, 200m, new DateOnly(2025, 5, 2));

    /// <summary>A stub real subject that counts how many calls actually reach it.</summary>
    private sealed class SpyPortfolio : IPortfolio
    {
        private readonly List<Lot> _lots = [];
        public int Reads { get; private set; }
        public int Writes { get; private set; }
        public Lot? LastAdded { get; private set; }

        public string Name { get { Reads++; return "Spy"; } }
        public IReadOnlyList<Lot> Lots { get { Reads++; return _lots; } }
        public void AddLot(Lot lot) { Writes++; LastAdded = lot; _lots.Add(lot); }
        public bool RemoveLot(Lot lot) { Writes++; return _lots.Remove(lot); }
    }

    [Fact]
    public void Advisor_AddLot_IsBlocked_AndNeverReachesTheRealPortfolio()
    {
        var real = new SpyPortfolio();
        IPortfolio proxy = new PortfolioAccessProxy(real, new User("Ion", Role.Advisor));

        Assert.Throws<AccessDeniedException>(() => proxy.AddLot(AppleLot()));
        Assert.Equal(0, real.Writes);
    }

    [Fact]
    public void Owner_AddLot_PassesTheSameLotThroughUnchanged()
    {
        var real = new SpyPortfolio();
        IPortfolio proxy = new PortfolioAccessProxy(real, new User("Adrian", Role.Owner));
        var lot = AppleLot();

        proxy.AddLot(lot);

        Assert.Equal(1, real.Writes);
        Assert.Same(lot, real.LastAdded);
    }

    [Fact]
    public void Advisor_Lots_ReturnsExactlyWhatTheRealPortfolioReturns()
    {
        var real = new Portfolio("Adrian", [AppleLot()]);
        IPortfolio proxy = new PortfolioAccessProxy(real, new User("Ion", Role.Advisor));

        Assert.Same(real.Lots, proxy.Lots);
        Assert.Equal(real.Name, proxy.Name);
    }

    [Fact]
    public void Guest_CannotEvenView()
    {
        var real = new SpyPortfolio();
        IPortfolio proxy = new PortfolioAccessProxy(real, new User("Visitor", Role.Guest));

        Assert.Throws<AccessDeniedException>(() => proxy.Lots);
        Assert.Throws<AccessDeniedException>(() => proxy.Name);
        Assert.Equal(0, real.Reads);
    }

    [Fact]
    public void EveryAttempt_IsRecordedInTheAccessLog()
    {
        var proxy = new PortfolioAccessProxy(new Portfolio("Adrian"), new User("Ion", Role.Advisor));

        _ = proxy.Lots;
        Assert.Throws<AccessDeniedException>(() => proxy.AddLot(AppleLot()));

        Assert.Collection(proxy.AccessLog,
            e => Assert.True(e.Allowed),
            e => Assert.Equal(("buy 3 AAPL", false), (e.Action, e.Allowed)));
    }

    [Fact]
    public void NewRole_WorksWithoutChangingTheProxy()
    {
        var auditor = new Role("Auditor", Permission.View);
        var real = new SpyPortfolio();
        IPortfolio proxy = new PortfolioAccessProxy(real, new User("Maria", auditor));

        _ = proxy.Lots;
        Assert.Throws<AccessDeniedException>(() => proxy.RemoveLot(AppleLot()));

        Assert.Equal(1, real.Reads);
        Assert.Equal(0, real.Writes);
    }
}
