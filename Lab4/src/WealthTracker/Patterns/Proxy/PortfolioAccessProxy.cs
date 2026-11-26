using WealthTracker.Domain;

namespace WealthTracker.Patterns.Proxy;

/// <summary>
/// PROXY - protection proxy. Implements the same <see cref="IPortfolio"/>
/// interface as the real portfolio and holds a reference to it. Before every
/// call it checks the user's role. An authorised call is forwarded unchanged;
/// an unauthorised one is logged and stopped here, so it never reaches the
/// real portfolio.
/// </summary>
public sealed class PortfolioAccessProxy : IPortfolio
{
    private readonly IPortfolio _real;
    private readonly User _user;
    private readonly List<AccessEvent> _log = [];

    public PortfolioAccessProxy(IPortfolio real, User user)
    {
        _real = real;
        _user = user;
    }

    /// <summary>Every attempt made through this proxy, allowed or not.</summary>
    public IReadOnlyList<AccessEvent> AccessLog => _log;

    public string Name
    {
        get
        {
            Demand(Permission.View, "view the portfolio");
            return _real.Name;
        }
    }

    public IReadOnlyList<Lot> Lots
    {
        get
        {
            Demand(Permission.View, "view the lots");
            return _real.Lots;
        }
    }

    public void AddLot(Lot lot)
    {
        ArgumentNullException.ThrowIfNull(lot);
        Demand(Permission.Trade, FormattableString.Invariant($"add a lot of {lot.Quantity} {lot.Instrument.Symbol}"));
        _real.AddLot(lot);
    }

    public bool RemoveLot(Lot lot)
    {
        ArgumentNullException.ThrowIfNull(lot);
        Demand(Permission.Trade, FormattableString.Invariant($"remove a lot of {lot.Quantity} {lot.Instrument.Symbol}"));
        return _real.RemoveLot(lot);
    }

    private void Demand(Permission permission, string action)
    {
        var allowed = _user.Role.Allows(permission);
        _log.Add(new AccessEvent(_user.Name, action, allowed));
        if (!allowed)
            throw new AccessDeniedException(_user, action);
    }
}
