namespace WealthTracker.Domain;

/// <summary>"Take <see cref="Quantity"/> units out of <see cref="Lot"/>" - one line of a sale.</summary>
public sealed record LotPick(Lot Lot, decimal Quantity);
