using WealthTracker.Client;

// dotnet run --project src/WealthTracker [console|markdown|csv]   scripted demo
// dotnet run --project src/WealthTracker -- shell                 try the Flyweight and the Proxy live
if (args is ["shell"])
{
    new LiveShell(Console.Out, DateOnly.FromDateTime(DateTime.Today)).Run(Console.In, prompt: true);
    return 0;
}
var format = args.Length > 0 ? args[0] : "console";
return ConsoleDemo.Run(format, Console.Out);
