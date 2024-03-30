using System.Net.WebSockets;

namespace Services;

public class TranscriptionService
{
    const string _route = "/transcription"; // API route

    // dependencies
    private readonly ILogger<TranscriptionService> _logger;
    private readonly string _websocket_route; // websocket route

    public bool IsTranscribing { get; private set; } = false;


    public TranscriptionService(Models.GlobalSettings globalSettings,
    ILogger<TranscriptionService> logger)
    {
        _websocket_route = globalSettings.BackendWSUrl + _route;
        _logger = logger;
    }

    public async Task ReceiveTextStreamAsync(Action<string> handler,
    CancellationToken cancellationToken = default)
    {
        IsTranscribing = true;
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
        catch (OperationCanceledException)
        {
            _logger.LogDebug("Transcription stream cancelled");
        }
        catch (WebSocketException)
        {
            _logger.LogInformation("Transcription stream closed");
        }
        finally
        {
            IsTranscribing = false;
            await socket.CloseAsync(CancellationToken.None);
        }
    }
}
