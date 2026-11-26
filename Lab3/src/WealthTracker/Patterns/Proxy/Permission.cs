namespace WealthTracker.Patterns.Proxy;

/// <summary>What a role may do with a portfolio. Flags, so roles combine them.</summary>
[Flags]
public enum Permission
{
    None = 0,
    View = 1,
    Trade = 2,
}
