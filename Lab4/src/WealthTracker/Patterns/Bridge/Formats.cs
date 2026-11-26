using System.Globalization;

namespace WealthTracker.Patterns.Bridge;

/// <summary>
/// Number formatting shared by all reports. Always uses the invariant culture,
/// so the output is identical on a Romanian, English or any other locale.
/// </summary>
internal static class Formats
{
    public static string Money(decimal value) =>
        value.ToString("#,##0.00", CultureInfo.InvariantCulture);

    /// <summary>Money with an explicit sign, for gains and losses: +12.50 / -3.00.</summary>
    public static string SignedMoney(decimal value) =>
        value.ToString("+#,##0.00;-#,##0.00;0.00", CultureInfo.InvariantCulture);

    public static string Quantity(decimal value) =>
        value.ToString("#,##0.########", CultureInfo.InvariantCulture);

    public static string Percent(decimal value) =>
        value.ToString("0.00", CultureInfo.InvariantCulture) + "%";
}
