using System.Text;

namespace WealthTracker.Patterns.Bridge;

/// <summary>
/// BRIDGE - concrete implementor: RFC 4180 CSV for spreadsheets. CSV has no
/// notion of a title, so <see cref="Title"/> renders nothing; fields become
/// two-column label,value rows.
/// </summary>
public sealed class CsvRenderer : IReportRenderer
{
    public string Title(string text) => string.Empty;

    public string Table(IReadOnlyList<Column> columns, IEnumerable<IReadOnlyList<string>> rows)
    {
        var text = new StringBuilder();
        text.AppendLine(Row(columns.Select(c => c.Header)));
        foreach (var row in rows)
            text.AppendLine(Row(row));
        return text.ToString();
    }

    public string Field(string label, string value) => Row([label, value]) + Environment.NewLine;

    private static string Row(IEnumerable<string> cells) => string.Join(',', cells.Select(Quote));

    // RFC 4180: a field containing a comma, quote or line break is wrapped in
    // quotes, and quotes inside it are doubled.
    private static string Quote(string cell) =>
        cell.IndexOfAny([',', '"', '\n', '\r']) >= 0
            ? "\"" + cell.Replace("\"", "\"\"") + "\""
            : cell;
}
