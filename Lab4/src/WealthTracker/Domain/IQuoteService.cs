namespace WealthTracker.Domain;

/// <summary>Current unit price of an instrument, in EUR.</summary>
public interface IQuoteService
{
    decimal PriceOf(string symbol);
}
