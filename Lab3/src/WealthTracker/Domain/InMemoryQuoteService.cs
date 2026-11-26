namespace WealthTracker.Domain;

/// <summary>
/// Deterministic prices for the demo and the unit tests. A live market-data
/// client would implement <see cref="IQuoteService"/> in exactly the same way.
/// </summary>
public sealed class InMemoryQuoteService : IQuoteService
{
    private readonly Dictionary<string, decimal> _prices;

    public InMemoryQuoteService(IReadOnlyDictionary<string, decimal> prices)
    {
        _prices = new Dictionary<string, decimal>(prices, StringComparer.OrdinalIgnoreCase);
    }

    public decimal PriceOf(string symbol) =>
        _prices.TryGetValue(symbol, out var price)
            ? price
            : throw new KeyNotFoundException($"No price available for '{symbol}'.");

    /// <summary>The same prices used in Labs 1 and 2, plus the VWCE ETF.</summary>
    public static InMemoryQuoteService Demo() => new(new Dictionary<string, decimal>
    {
        ["AAPL"] = 214.50m,
        ["MSFT"] = 432.10m,
        ["VWCE"] = 118.40m,
        ["BTC"] = 61_250.00m,
        ["ETH"] = 2_980.75m,
        ["EUR-CASH"] = 1.00m,
    });
}
