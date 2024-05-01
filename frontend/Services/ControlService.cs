namespace Services;

public class ControlService
{
    const string _route = "api/control"; // API route

    // dependencies
    private readonly HttpClient _httpClient; // used to call API
    private readonly ILogger<ControlService> _logger;
    private readonly string _http_route; // API http route


    public ControlService(HttpClient httpClient,
    Models.GlobalSettings globalSettings, ILogger<ControlService> logger)
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

    public async Task DriveForwardAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.PostAsync(_http_route + "/forward", null);
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to drive forward");
            throw;
        }
    }

    public async Task StopForwardAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.DeleteAsync(_http_route + "/forward");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to stop driving forward");
            throw;
        }
    }

    public async Task DriveBackwardAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.PostAsync(_http_route + "/backward", null);
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to drive backward");
            throw;
        }
    }

    public async Task StopBackwardAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.DeleteAsync(_http_route + "/backward");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to stop driving backward");
            throw;
        }
    }

    public async Task TurnLeftAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.PostAsync(_http_route + "/left", null);
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to turn left");
            throw;
        }
    }

    public async Task StopLeftAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.DeleteAsync(_http_route + "/left");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to stop turning left");
            throw;
        }
    }

    public async Task TurnRightAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.PostAsync(_http_route + "/right", null);
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to turn right");
            throw;
        }
    }

    public async Task StopRightAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.DeleteAsync(_http_route + "/right");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to stop turning right");
            throw;
        }
    }

    public async Task OnSirenAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.PostAsync(_http_route + "/siren", null);
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to enable Siren");
            throw;
        }
    }

    public async Task OffSirenAsync()
    {
        try
        {
            using HttpResponseMessage response = await _httpClient.DeleteAsync(_http_route + "/siren");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to enable Siren");
            throw;
        }
    }
}
