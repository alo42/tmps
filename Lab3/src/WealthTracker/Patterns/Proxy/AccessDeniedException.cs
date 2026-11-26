namespace WealthTracker.Patterns.Proxy;

/// <summary>Thrown by the proxy when the user's role lacks the required permission.</summary>
public sealed class AccessDeniedException : Exception
{
    public AccessDeniedException(User user, string action)
        : base($"{user.Name} ({user.Role.Name}) is not allowed to {action}.")
    {
        User = user;
        Action = action;
    }

    public User User { get; }
    public string Action { get; }
}
