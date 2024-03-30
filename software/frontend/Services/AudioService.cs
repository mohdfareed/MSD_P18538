using System.Net.WebSockets;
using Microsoft.JSInterop;

namespace Services;

public class AudioService
{
    const string _route = "/audio"; // API route

    // dependencies
    private readonly IJSRuntime _jsRuntime;
    private readonly DotNetObjectReference<AudioService> _objRef;
    private readonly ILogger<AudioService> _logger;
    private readonly string _websocket_route;

    // state
    private WebSocketConnection? _socket = null;
    private CancellationToken? _cancellationToken = null;
    public bool IsRecording { get; private set; } = false;


    public AudioService(Models.GlobalSettings globalSettings,
    IJSRuntime JSRuntime, ILogger<AudioService> logger)
    {
        _websocket_route = globalSettings.BackendWSUrl + _route;
        _jsRuntime = JSRuntime;
        _objRef = DotNetObjectReference.Create(this);
        _logger = logger;
    }

    public async Task StartAudioStreamingAsync(
    CancellationToken cancellationToken = default)
    {
        IsRecording = true;
        _cancellationToken = cancellationToken;
        _socket = new WebSocketConnection();

        try
        {
            await _socket.ConnectAsync(_websocket_route, cancellationToken);
            await _jsRuntime.InvokeVoidAsync("record", _objRef, "Callback");
        }
        catch (WebSocketException ex)
        {
            _logger.LogError(ex, "Failed to start audio streaming");
        }
    }

    [JSInvokable]
    public async Task Callback(byte[] audioData)
    {
        try
        {
            if (_cancellationToken?.IsCancellationRequested ?? true)
            {
                throw new OperationCanceledException();
            }
            await _socket!.SendAsync(audioData);
        }
        catch
        {
            _logger.LogInformation("Mic connection closed");
            IsRecording = false;
            _cancellationToken = null;

            await _jsRuntime.InvokeVoidAsync("stopRecording");
            if (_socket != null)
            {
                await _socket.CloseAsync();
                _socket = null;
            }
        }
    }
}