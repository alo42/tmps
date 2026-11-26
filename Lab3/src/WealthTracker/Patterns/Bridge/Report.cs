using WealthTracker.Domain;

namespace WealthTracker.Patterns.Bridge;

/// <summary>
/// BRIDGE - the abstraction. Decides <i>what</i> a report contains and
/// delegates <i>how</i> it is drawn to the renderer it holds. Reports and
/// formats vary independently: N reports and M formats need N + M classes,
/// not N x M.
/// </summary>
public abstract class Report
{
    protected Report(IReportRenderer renderer)
    {
        Renderer = renderer ?? throw new ArgumentNullException(nameof(renderer));
    }

    /// <summary>The bridge to the implementation side.</summary>
    protected IReportRenderer Renderer { get; }

    protected abstract string Heading { get; }

    public string Render(IPortfolio portfolio, IQuoteService quotes) =>
        Renderer.Title($"{Heading} - {portfolio.Name}") + Body(portfolio, quotes);

    protected abstract string Body(IPortfolio portfolio, IQuoteService quotes);
}
