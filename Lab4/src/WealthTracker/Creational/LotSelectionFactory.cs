using WealthTracker.Patterns.Strategy;

namespace WealthTracker.Creational;

/// <summary>
/// FACTORY METHOD - parameterised, like <see cref="RendererFactory"/>. Turns the
/// name a user types ("fifo") into a lot-selection strategy. Methods are
/// registered, so a new one never edits this class.
/// </summary>
public sealed class LotSelectionFactory
{
    private readonly Dictionary<string, Func<ILotSelectionStrategy>> _creators = new(StringComparer.OrdinalIgnoreCase);

    public IEnumerable<string> KnownMethods => _creators.Keys.Order();

    public LotSelectionFactory Register(string name, Func<ILotSelectionStrategy> creator)
    {
        _creators[name] = creator;
        return this;
    }

    public ILotSelectionStrategy Create(string name) =>
        _creators.TryGetValue(name, out var create)
            ? create()
            : throw new ArgumentException(
                $"Unknown lot-selection method '{name}'. Known methods: {string.Join(", ", KnownMethods)}.", nameof(name));

    public static LotSelectionFactory Default() => new LotSelectionFactory()
        .Register("fifo", () => new FifoSelection())
        .Register("lifo", () => new LifoSelection())
        .Register("hifo", () => new HighestCostSelection());
}
