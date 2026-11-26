using WealthTracker.Client;

// dotnet run --project src/WealthTracker            scripted demo of every pattern
// dotnet run --project src/WealthTracker -- shell   type the commands yourself
return args is ["shell"]
    ? ConsoleDemo.Interactive(Console.In, Console.Out, DateOnly.FromDateTime(DateTime.Today))
    : ConsoleDemo.Run(Console.Out);
