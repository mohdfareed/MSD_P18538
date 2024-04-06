using System.Text.Json;

namespace Services;

public class ControllerService
{
    const string _route = "controller"; // API route

    // dependencies
    private readonly HttpClient _httpClient; // used to call API
    private readonly ILogger<ConfigurationService> _logger;
    // routes
    private readonly string _http_route; // API http route

    public ControllerService(HttpClient httpClient,
    Models.GlobalSettings globalSettings, ILogger<ConfigurationService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        var builder = new UriBuilder(httpClient.BaseAddress!)
        {
            Port = int.Parse(globalSettings.BackendPort),
            Path = _route
        };
        _http_route = builder.Uri.ToString();
    }

    public async Task SendCommandAsync(Models.Movement movement)
    {
        try 
        {
            var json = JsonSerializer.Serialize(movement);
            using StringContent content = new(json, System.Text.Encoding.UTF8, "applications/json");
            using HttpResponseMessage response = await _httpClient.PostAsync(_http_route, content);
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to set configuration");
            throw;
        }
    }
}