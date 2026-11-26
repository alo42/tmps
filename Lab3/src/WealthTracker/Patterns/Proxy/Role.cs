namespace WealthTracker.Patterns.Proxy;

/// <summary>
/// A named set of permissions. Roles are data, not subclasses: a new role
/// (for example an auditor) is created without editing this class or the proxy.
/// </summary>
public sealed record Role(string Name, Permission Permissions)
{
    public static readonly Role Owner = new("Owner", Permission.View | Permission.Trade);
    public static readonly Role Advisor = new("Advisor", Permission.View);
    public static readonly Role Guest = new("Guest", Permission.None);

    public bool Allows(Permission permission) => (Permissions & permission) == permission;
}
