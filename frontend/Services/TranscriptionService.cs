using System.Net.WebSockets;

namespace Services;

public class TranscriptionService
{
    const string _route = "api/transcription"; // API route

    // dependencies
    private readonly ILogger<TranscriptionService> _logger;
    private readonly string _websocket_route;
    private Action? _cancelCallback = null;


    public TranscriptionService(HttpClient httpClient,
    Models.GlobalSettings globalSettings, ILogger<TranscriptionService> logger)
    {
        _logger = logger;

        var builder = new UriBuilder(httpClient.BaseAddress!)
        {
            Scheme = httpClient.BaseAddress!.Scheme == "https" ? "wss" : "ws",
            Port = int.Parse(globalSettings.BackendPort),
            Path = _route
        };
        _websocket_route = builder.Uri.ToString();
    }

    public async Task ReceiveTextStreamAsync(Action<string> handler,
    Action cancelCallback, CancellationToken cancellationToken = default)
    {
        _cancelCallback = cancelCallback;
        WebSocketConnection socket = new();
        string? message;

        try
        {
            await socket.ConnectAsync(_websocket_route, cancellationToken);
            while (true)
            {
                message = await socket.ReceiveAsync<string>(cancellationToken);
                if (message == null) break;
                handler(message);
            }
        }
        catch (WebSocketException)
        {
            _logger.LogInformation("Transcription stream closed");
        }
        finally
        {
            _cancelCallback?.Invoke();
            _cancelCallback = null;
            await socket.CloseAsync(CancellationToken.None);
        }
    }
}
