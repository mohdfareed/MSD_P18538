using System.Net.Http.Json;
using System.Net.WebSockets;
using System.Text.Json;
using Microsoft.JSInterop;

namespace Services;

public class ControllerService
{
    const string _route = "/controller/"; // API route

    // dependencies
    private readonly DotNetObjectReference<ConfigurationService> _objRef;
    private readonly HttpClient _httpClient; // used to call API
    private readonly ILogger<ConfigurationService> _logger;

    // routes
    private readonly string _http_route; // API http route

    public ControllerService(HttpClient httpClient,
    Models.GlobalSettings globalSettings, ILogger<ConfigurationService> logger)
    {
        _httpClient = httpClient;
        _http_route = globalSettings.BackendHTTPUrl + _route;

        // _objRef = DotNetObjectReference.Create(this);
        _logger = logger;
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