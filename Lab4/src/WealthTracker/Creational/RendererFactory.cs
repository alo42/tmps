using WealthTracker.Patterns.Bridge;

namespace WealthTracker.Creational;

/// <summary>
/// FACTORY METHOD - parameterised variant (reused from Lab 2). Creates the
/// renderer for a format name such as "markdown". Formats are registered
/// rather than listed in a switch, so supporting a new one never edits this class.
/// </summary>
public sealed class RendererFactory
{
    private readonly Dictionary<string, Func<IReportRenderer>> _creators = new(StringComparer.OrdinalIgnoreCase);

    public IEnumerable<string> KnownFormats => _creators.Keys.Order();

    public RendererFactory Register(string format, Func<IReportRenderer> creator)
    {
        _creators[format] = creator;
        return this;
    }

    public IReportRenderer Create(string format) =>
        _creators.TryGetValue(format, out var create)
            ? create()
            : throw new ArgumentException(
                $"Unknown format '{format}'. Known formats: {string.Join(", ", KnownFormats)}.", nameof(format));

    public static RendererFactory Default() => new RendererFactory()
        .Register("console", () => new ConsoleTableRenderer())
        .Register("markdown", () => new MarkdownRenderer())
        .Register("csv", () => new CsvRenderer());
}
