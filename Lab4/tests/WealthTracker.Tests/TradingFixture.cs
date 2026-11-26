using WealthTracker.Domain;
using WealthTracker.Patterns.Flyweight;
using WealthTracker.Patterns.Strategy;

namespace WealthTracker.Tests;

/// <summary>
/// A small portfolio with three ETH lots whose order by date differs from their
/// order by cost, so FIFO, LIFO and HIFO each pick different lots.
/// </summary>
internal sealed class TradingFixture
{
    public const decimal EthPrice = 2_980.75m;
    public static readonly DateOnly Today = new(2026, 11, 26);

    public TradingFixture(ILotSelectionStrategy? lotSelection = null)
    {
        Instruments = new InstrumentFactory(InstrumentCatalog.Default());
        Oldest = new Lot(Instruments.Get("ETH"), 4.2m, 1_850m, new DateOnly(2023, 3, 12));
        Priciest = new Lot(Instruments.Get("ETH"), 1.5m, 3_900m, new DateOnly(2024, 3, 11));
        Newest = new Lot(Instruments.Get("ETH"), 2.0m, 2_300m, new DateOnly(2024, 8, 5));
        Apple = new Lot(Instruments.Get("AAPL"), 8m, 150m, new DateOnly(2022, 3, 15));
        Portfolio = new Portfolio("Test", [Oldest, Priciest, Newest, Apple]);
        Account = new TradingAccount(Portfolio, Instruments, lotSelection ?? new FifoSelection());
    }

    public InstrumentFactory Instruments { get; }
    public Portfolio Portfolio { get; }
    public TradingAccount Account { get; }
    public Lot Oldest { get; }
    public Lot Priciest { get; }
    public Lot Newest { get; }
    public Lot Apple { get; }

    public IReadOnlyList<Lot> EthLots => [Oldest, Priciest, Newest];
}
