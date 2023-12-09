using System.Net.WebSockets;
using System.Text.Json;
using Microsoft.JSInterop;

namespace Services;

public class TranscriptionService
{
    const string _route = "/transcription/"; // API route

    // dependencies
    private readonly IJSRuntime _jsRuntime;
    private readonly DotNetObjectReference<TranscriptionService> _objRef;
    private readonly HttpClient _httpClient; // used to call API
    private readonly ILogger<TranscriptionService> _logger;

    // routes
    private readonly string _http_route; // API http route
    private readonly string _websocket_route; // websocket route

    // state
    private WebSocketConnection? _socket = null;
    private Action? _micCancellationTask = null;


    public TranscriptionService(HttpClient httpClient,
    Models.GlobalSettings globalSettings, IJSRuntime JSRuntime,
    ILogger<TranscriptionService> logger, IServiceProvider serviceProvider)
    {
        _httpClient = httpClient;
        _http_route = globalSettings.BackendHTTPUrl + _route;
        _websocket_route = globalSettings.BackendWSUrl + _route;

        _jsRuntime = JSRuntime;
        _objRef = DotNetObjectReference.Create(this);
        _logger = logger;
    }

    public async Task ReceiveTextStreamAsync(Action<string> handler,
        CancellationToken cancellationToken = default)
    {
        WebSocketConnection socket = new();
        string? message;


        try
        {
            await socket.ConnectAsync(_websocket_route + "stream",
            cancellationToken);

            message = await socket.ReceiveAsync<string>(cancellationToken);
            while (message != null)
            {
                handler(message);
                message = await socket.ReceiveAsync<string>(cancellationToken);
            };
        }
        catch (OperationCanceledException)
        {
            _logger.LogDebug("Transcription stream cancelled");
        }
        catch (WebSocketException ex)
        {
            _logger.LogError(ex,
            "Websocket error occurred receiving transcription");
        }
    }

    public async Task StartAudioStreamingAsync(Action cancellationAction,
    CancellationToken cancellationToken = default)
    {
        _socket = new WebSocketConnection();
        _micCancellationTask = cancellationAction;
        cancellationToken.Register(async () =>
        {
            await _jsRuntime.InvokeVoidAsync("stopRecording");
            await _socket.CloseAsync();
            _micCancellationTask = null;
            _socket = null;
            _logger.LogDebug("Audio streaming cancelled");
        });

        try
        {
            await _socket.ConnectAsync(_websocket_route + "start", cancellationToken);
            await _jsRuntime.InvokeVoidAsync("startRecording", _objRef,
            "AudioCaptureCallback", "AudioConfigCallback");
        }
        catch (OperationCanceledException)
        {
            _logger.LogDebug("Audio streaming cancelled");
        }
        catch (WebSocketException ex)
        {
            _logger.LogError(ex, "Unknown error occurred initiating streaming");
            _micCancellationTask?.Invoke();
        }
    }

    [JSInvokable]
    public async Task AudioConfigCallback(string config)
    {
        try
        {
            if (_socket == null) return;
            var micConfig = JsonSerializer.Deserialize<Models.MicConfig>(config)!;
            await _socket.SendAsync(micConfig);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unknown error occurred configuring mic");
            _micCancellationTask?.Invoke();
        }
    }

    [JSInvokable]
    public async Task AudioCaptureCallback(byte[] audioData)
    {
        try
        {
            if (_socket == null) return;
            await _socket.SendAsync(audioData);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unknown error occurred capturing audio");
            _micCancellationTask?.Invoke();
        }
    }
}
