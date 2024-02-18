namespace Models;

public class GlobalSettings
{
    public string? BackendAddr { get; set; }
    public string? BackendPort { get; set; }

    public string BackendHTTPUrl => $"http://{BackendAddr!}:{BackendPort!}";
    public string BackendWSUrl => $"ws://{BackendAddr!}:{BackendPort!}";
}
