using System.Net.WebSockets;

namespace Services;

public class TranscriptionService
{
    const string _route = "/transcription"; // API route

    // dependencies
    private readonly ILogger<TranscriptionService> _logger;
    private readonly string _websocket_route;
    private Action? _cancelCallback = null;


    public TranscriptionService(Models.GlobalSettings globalSettings,
    ILogger<TranscriptionService> logger)
    {
        _websocket_route = globalSettings.BackendWSUrl + _route;
        _logger = logger;
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
