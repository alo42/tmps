using WealthTracker.Creational;
using WealthTracker.Domain;
using WealthTracker.Patterns.Strategy;

namespace WealthTracker.Tests;

public class StrategyTests
{
    [Fact]
    public void Fifo_SellsTheOldestLotFirst()
    {
        var f = new TradingFixture();

        var picks = new FifoSelection().Select(f.EthLots, 2m);

        Assert.Equal([new LotPick(f.Oldest, 2m)], picks);
    }

    [Fact]
    public void Lifo_SellsTheNewestLotFirst()
    {
        var f = new TradingFixture();

        var picks = new LifoSelection().Select(f.EthLots, 2m);

        Assert.Equal([new LotPick(f.Newest, 2m)], picks);
    }

    [Fact]
    public void HighestCost_SellsTheMostExpensiveLotsFirst()
    {
        var f = new TradingFixture();

        var picks = new HighestCostSelection().Select(f.EthLots, 2m);

        Assert.Equal([new LotPick(f.Priciest, 1.5m), new LotPick(f.Newest, 0.5m)], picks);
    }

    [Theory]
    [InlineData("fifo", "2261.50")]   // 2 x (2,980.75 - 1,850)
    [InlineData("lifo", "1361.50")]   // 2 x (2,980.75 - 2,300)
    [InlineData("hifo", "-1038.50")]  // 1.5 x (2,980.75 - 3,900) + 0.5 x (2,980.75 - 2,300)
    public void SameSale_RealisesADifferentGain_UnderEachMethod(string method, string expectedGain)
    {
        var f = new TradingFixture(LotSelectionFactory.Default().Create(method));

        var receipt = f.Account.Sell("ETH", 2m, TradingFixture.EthPrice, TradingFixture.Today);

        Assert.Equal(decimal.Parse(expectedGain, System.Globalization.CultureInfo.InvariantCulture),
                     receipt.Trade.RealisedGain);
        Assert.Equal(method.ToUpperInvariant(), receipt.Trade.Method);
    }

    [Fact]
    public void SwitchingTheMethodAtRuntime_ChangesWhichLotsTheNextSaleUses()
    {
        var f = new TradingFixture(new FifoSelection());
        var first = f.Account.Sell("ETH", 1m, TradingFixture.EthPrice, TradingFixture.Today);

        f.Account.UseLotSelection(new LifoSelection());              // same account, new behaviour
        var second = f.Account.Sell("ETH", 1m, TradingFixture.EthPrice, TradingFixture.Today);

        Assert.Same(f.Oldest, first.Trade.Picks.Single().Lot);
        Assert.Same(f.Newest, second.Trade.Picks.Single().Lot);
    }

    [Fact]
    public void Sale_SpansLots_AndKeepsTheUnsoldRestAtItsOriginalCostAndDate()
    {
        var f = new TradingFixture(new FifoSelection());

        var receipt = f.Account.Sell("ETH", 5m, TradingFixture.EthPrice, TradingFixture.Today);

        Assert.Equal([f.Oldest, f.Priciest], receipt.Removed);           // 4.2 + 0.8 of 1.5
        var rest = Assert.Single(receipt.Added);
        Assert.Equal((0.7m, 3_900m, new DateOnly(2024, 3, 11)), (rest.Quantity, rest.UnitCost, rest.Purchased));
        Assert.Equal(7.7m - 5m, f.Account.QuantityHeld("ETH"));
    }

    [Fact]
    public void SellingMoreThanHeld_Throws_AndChangesNothing()
    {
        var f = new TradingFixture();

        Assert.Throws<InvalidOperationException>(() => f.Account.Sell("ETH", 8m, 1m, TradingFixture.Today));
        Assert.Equal([f.Oldest, f.Priciest, f.Newest, f.Apple], f.Portfolio.Lots);
    }

    /// <summary>A method the project does not have, written only here.</summary>
    private sealed class LargestLotFirst : ILotSelectionStrategy
    {
        public string Name => "LARGEST";
        public IReadOnlyList<LotPick> Select(IReadOnlyList<Lot> lots, decimal quantity) =>
            LotPicking.TakeInOrder(lots.OrderByDescending(lot => lot.Quantity), quantity);
    }

    [Fact]
    public void NewMethod_PlugsIn_WithoutChangingTheAccountOrTheFactory()
    {
        var factory = LotSelectionFactory.Default().Register("largest", () => new LargestLotFirst());
        var f = new TradingFixture(factory.Create("largest"));

        var receipt = f.Account.Sell("ETH", 5m, TradingFixture.EthPrice, TradingFixture.Today);

        Assert.Equal([new LotPick(f.Oldest, 4.2m), new LotPick(f.Newest, 0.8m)], receipt.Trade.Picks);
        Assert.Contains("largest", factory.KnownMethods);
    }

    [Fact]
    public void LotSelectionFactory_UnknownMethod_ListsTheKnownOnes()
    {
        var ex = Assert.Throws<ArgumentException>(() => LotSelectionFactory.Default().Create("random"));

        Assert.Contains("fifo, hifo, lifo", ex.Message);
    }
}
