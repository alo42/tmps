namespace WealthTracker.Patterns.Bridge;

/// <summary>A table column; numeric columns are right-aligned where the format allows it.</summary>
public sealed record Column(string Header, bool Numeric = false);

/// <summary>
/// BRIDGE - the implementor. The low-level drawing primitives every output
/// format must provide. Reports are written only against these three methods.
/// </summary>
public interface IReportRenderer
{
    string Title(string text);
    string Table(IReadOnlyList<Column> columns, IEnumerable<IReadOnlyList<string>> rows);
    string Field(string label, string value);
}
