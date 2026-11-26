using System.Text;

namespace WealthTracker.Patterns.Bridge;

/// <summary>BRIDGE - concrete implementor: GitHub-flavoured Markdown.</summary>
public sealed class MarkdownRenderer : IReportRenderer
{
    public string Title(string text) => $"## {Escape(text)}\n\n";

    public string Table(IReadOnlyList<Column> columns, IEnumerable<IReadOnlyList<string>> rows)
    {
        var text = new StringBuilder();
        text.Append("| ").Append(string.Join(" | ", columns.Select(c => Escape(c.Header)))).AppendLine(" |");
        text.Append('|').Append(string.Join('|', columns.Select(c => c.Numeric ? " ---: " : " --- "))).AppendLine("|");
        foreach (var row in rows)
            text.Append("| ").Append(string.Join(" | ", row.Select(Escape))).AppendLine(" |");
        return text.AppendLine().ToString();
    }

    public string Field(string label, string value) => $"**{Escape(label)}:** {Escape(value)}  \n";

    // A literal pipe would end the table cell.
    private static string Escape(string text) => text.Replace("|", "\\|");
}
