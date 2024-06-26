using System.Text.Json;

namespace Services;

public class ConfigurationService
{
    const string _route = "api/config"; // API route

    // dependencies
    private readonly HttpClient _httpClient; // used to call API
    private readonly ILogger<ConfigurationService> _logger;
    private readonly string _http_route; // API http route


    public ConfigurationService(HttpClient httpClient,
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

    public async Task<Models.Config> GetConfigAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync(_http_route);
            response.EnsureSuccessStatusCode();
            var responseString = await response.Content.ReadAsStringAsync();
            var config = JsonSerializer.Deserialize<Models.Config>(responseString);
            return config!;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to get configuration");
            throw;
        }
    }

    public async Task SetConfigAsync(Models.Config config)
    {
        try
        {
            var json = JsonSerializer.Serialize(config);
            using StringContent content = new(json, System.Text.Encoding.UTF8, "application/json");
            using HttpResponseMessage response = await _httpClient.PostAsync(_http_route, content);
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to set configuration");
            throw;
        }
    }

    public async Task<Dictionary<int, string>> GetAudioDevicesAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync($"{_http_route}/audio_devices");
            response.EnsureSuccessStatusCode();
            var responseString = await response.Content.ReadAsStringAsync();
            var audioDevices = JsonSerializer.Deserialize<Dictionary<int, string>>(responseString);
            return audioDevices!;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to get audio devices");
            throw;
        }
    }
}
