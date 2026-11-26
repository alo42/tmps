using WealthTracker.Domain;
using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Creational;

/// <summary>
/// BUILDER (reused from Lab 2). Builds a portfolio step by step through a
/// fluent API. Every instrument comes from the flyweight factory, so anything
/// the builder produces shares instruments automatically.
/// </summary>
public sealed class PortfolioBuilder
{
    private readonly InstrumentFactory _instruments;
    private readonly List<Lot> _lots = [];
    private string _name = "Portfolio";

    public PortfolioBuilder(InstrumentFactory instruments)
    {
        _instruments = instruments;
    }

    public PortfolioBuilder Named(string name)
    {
        _name = name;
        return this;
    }

    public PortfolioBuilder Buy(string symbol, decimal quantity, decimal unitCost, DateOnly date)
    {
        _lots.Add(new Lot(_instruments.Get(symbol), quantity, unitCost, date));
        return this;
    }

    /// <summary>
    /// Dollar-cost averaging: the same purchase every month. This is why a real
    /// portfolio holds hundreds of lots of one instrument, which is the
    /// situation the Flyweight is designed for.
    /// </summary>
    public PortfolioBuilder BuyMonthly(string symbol, decimal quantity, decimal firstCost,
                                       decimal monthlyCostChange, DateOnly start, int months)
    {
        for (var month = 0; month < months; month++)
            Buy(symbol, quantity, firstCost + monthlyCostChange * month, start.AddMonths(month));
        return this;
    }

    /// <summary>Returns the finished portfolio and resets the builder for reuse.</summary>
    public IPortfolio Build()
    {
        if (_lots.Count == 0)
            throw new InvalidOperationException("A portfolio needs at least one lot.");

        var portfolio = new Portfolio(_name, _lots);
        _lots.Clear();
        _name = "Portfolio";
        return portfolio;
    }
}
