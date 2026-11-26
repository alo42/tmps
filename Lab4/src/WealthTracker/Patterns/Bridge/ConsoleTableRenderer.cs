using System.Text;

namespace WealthTracker.Patterns.Bridge;

/// <summary>BRIDGE - concrete implementor: aligned plain-text tables for the terminal.</summary>
public sealed class ConsoleTableRenderer : IReportRenderer
{
    private const string Gap = "  ";

    public string Title(string text) =>
        $"{text}{Environment.NewLine}{new string('=', text.Length)}{Environment.NewLine}";

    public string Table(IReadOnlyList<Column> columns, IEnumerable<IReadOnlyList<string>> rows)
    {
        var data = rows.ToList();
        var widths = columns
            .Select((c, i) => data.Select(r => r[i].Length).Append(c.Header.Length).Max())
            .ToArray();

        var text = new StringBuilder();
        text.AppendLine(Line(columns.Select(c => c.Header).ToList(), columns, widths));
        text.AppendLine(string.Join(Gap, widths.Select(w => new string('-', w))));
        foreach (var row in data)
            text.AppendLine(Line(row, columns, widths));
        return text.ToString();
    }

    public string Field(string label, string value) =>
        $"{(label + ":").PadRight(18)}{value}{Environment.NewLine}";

    private static string Line(IReadOnlyList<string> cells, IReadOnlyList<Column> columns, int[] widths) =>
        string.Join(Gap, cells.Select((cell, i) =>
            columns[i].Numeric ? cell.PadLeft(widths[i]) : cell.PadRight(widths[i]))).TrimEnd();
}
