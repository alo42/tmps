using WealthTracker.Client;

// Usage: dotnet run --project src/WealthTracker [console|markdown|csv]
var format = args.Length > 0 ? args[0] : "console";
return ConsoleDemo.Run(format, Console.Out);
