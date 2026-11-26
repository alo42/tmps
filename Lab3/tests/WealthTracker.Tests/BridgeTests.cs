using WealthTracker.Domain;
using WealthTracker.Patterns.Bridge;
using WealthTracker.Patterns.Flyweight;

namespace WealthTracker.Tests;

public class BridgeTests
{
    private static readonly IQuoteService Quotes = InMemoryQuoteService.Demo();
    private static readonly IPortfolio Portfolio =
        TestData.DemoPortfolio(new InstrumentFactory(InstrumentCatalog.Default()));

    /// <summary>A test-only format: records which primitives a report used.</summary>
    private sealed class RecordingRenderer : IReportRenderer
    {
        public List<string> Calls { get; } = [];
        public string Title(string text) { Calls.Add("Title"); return ""; }
        public string Table(IReadOnlyList<Column> columns, IEnumerable<IReadOnlyList<string>> rows)
        {
            Calls.Add($"Table({rows.Count()} rows)");
            return "";
        }
        public string Field(string label, string value) { Calls.Add($"Field({label})"); return ""; }
    }

    /// <summary>A test-only report: counts lots per symbol.</summary>
    private sealed class LotCountReport(IReportRenderer renderer) : Report(renderer)
    {
        protected override string Heading => "Lots";
        protected override string Body(IPortfolio portfolio, IQuoteService quotes) =>
            Renderer.Table([new Column("Symbol"), new Column("Lots", Numeric: true)],
                portfolio.Lots.GroupBy(l => l.Instrument.Symbol)
                    .Select(g => (IReadOnlyList<string>)[g.Key, g.Count().ToString()]));
    }

    public static TheoryData<IReportRenderer> AllRenderers() =>
        [new ConsoleTableRenderer(), new MarkdownRenderer(), new CsvRenderer()];

    [Theory]
    [MemberData(nameof(AllRenderers))]
    public void HoldingsReport_ShowsTheSameTotal_InEveryFormat(IReportRenderer renderer)
    {
        var output = new HoldingsReport(renderer).Render(Portfolio, Quotes);

        Assert.Contains(TestData.TotalValue, output);
        Assert.Contains("VWCE", output);
    }

    [Fact]
    public void NewRenderer_WorksWithEveryReport_WithoutChangingThem()
    {
        var reports = new Func<IReportRenderer, Report>[]
            { r => new HoldingsReport(r), r => new AllocationReport(r), r => new PerformanceReport(r) };

        foreach (var create in reports)
        {
            var recorder = new RecordingRenderer();
            create(recorder).Render(Portfolio, Quotes);
            Assert.Equal("Title", recorder.Calls[0]);
            Assert.True(recorder.Calls.Count > 1);
        }
    }

    [Theory]
    [MemberData(nameof(AllRenderers))]
    public void NewReport_WorksWithEveryRenderer_WithoutChangingThem(IReportRenderer renderer)
    {
        var output = new LotCountReport(renderer).Render(Portfolio, Quotes);

        Assert.Contains("VWCE", output);
        Assert.Contains("36", output); // 36 monthly VWCE purchases
    }

    [Fact]
    public void HoldingsReport_AggregatesLotsPerInstrument()
    {
        var recorder = new RecordingRenderer();

        new HoldingsReport(recorder).Render(Portfolio, Quotes);

        Assert.Contains("Table(6 rows)", recorder.Calls); // 43 lots, 6 instruments
    }

    [Fact]
    public void CsvRenderer_QuotesFieldsContainingCommas()
    {
        var csv = new CsvRenderer().Table([new Column("Name"), new Column("Value")],
                                          [["Apple, Inc.", "2,574.00"], ["Say \"hi\"", "1"]]);

        Assert.Contains("\"Apple, Inc.\",\"2,574.00\"", csv);
        Assert.Contains("\"Say \"\"hi\"\"\",1", csv);
    }

    [Fact]
    public void MarkdownRenderer_RightAlignsNumericColumns()
    {
        var md = new MarkdownRenderer().Table([new Column("Symbol"), new Column("Value", Numeric: true)],
                                              [["BTC", "21,437.50"]]);

        Assert.Contains("| --- | ---: |", md);
    }

    [Fact]
    public void PerformanceReport_ComputesTheReturnOnCost()
    {
        var output = new PerformanceReport(new ConsoleTableRenderer()).Render(Portfolio, Quotes);

        Assert.Contains(TestData.TotalCost, output);
        Assert.Contains("30.72%", output); // (54,715.95 - 41,856.80) / 41,856.80
    }
}
