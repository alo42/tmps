namespace WealthTracker.Patterns.Proxy;

/// <summary>One entry of the proxy's access log.</summary>
public sealed record AccessEvent(string User, string Action, bool Allowed);
