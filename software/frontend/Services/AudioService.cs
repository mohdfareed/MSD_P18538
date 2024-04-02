using Microsoft.JSInterop;

namespace Services;

public class AudioService
{
    const string _route = "audio"; // API route

    // dependencies
    private readonly IJSRuntime _jsRuntime;
    private readonly DotNetObjectReference<AudioService> _objRef;
    private readonly ILogger<AudioService> _logger;
    private readonly string _websocket_route;

    // state
    private WebSocketConnection? _socket = null;
    private CancellationToken? _cancellationToken = null;
    private Action? _cancelCallback = null;


    public AudioService(HttpClient httpClient,
    Models.GlobalSettings globalSettings, IJSRuntime JSRuntime,
    ILogger<AudioService> logger)
    {
        _jsRuntime = JSRuntime;
        _objRef = DotNetObjectReference.Create(this);
        _logger = logger;

        var builder = new UriBuilder(httpClient.BaseAddress!)
        {
            Scheme = httpClient.BaseAddress!.Scheme == "https" ? "wss" : "ws",
            Port = int.Parse(globalSettings.BackendPort),
            Path = _route,
        };
        _websocket_route = builder.Uri.ToString();
    }

    public async Task StartAudioStreamingAsync(Action cancelCallback,
    CancellationToken cancellationToken = default)
    {
        _cancelCallback = cancelCallback;
        _cancellationToken = cancellationToken;
        _socket = new WebSocketConnection();

        await _socket.ConnectAsync(_websocket_route, cancellationToken);
        await _jsRuntime.InvokeVoidAsync("record", _objRef,
        "Callback", "ConfigCallback");
    }

    [JSInvokable]
    public async Task Callback(byte[] audioData)
    {
        try
        {
            if (_socket == null) return;
            if (_cancellationToken?.IsCancellationRequested ?? true)
            {
                throw new OperationCanceledException();
            }
            await _socket!.SendAsync(audioData);
        }
        catch
        {
            _logger.LogInformation("Mic connection closed");
            _cancellationToken = null;
            _cancelCallback?.Invoke();
            _cancelCallback = null;

            await _jsRuntime.InvokeVoidAsync("stopRecording");
            if (_socket != null)
            {
                await _socket.CloseAsync();
                _socket = null;
            }
        }
    }

    [JSInvokable]
    public async Task ConfigCallback(int sampleRate, int sampleWidth,
    int channelCount)
    {
        try
        {
            if (_socket == null) return;
            if (_cancellationToken?.IsCancellationRequested ?? true)
            {
                throw new OperationCanceledException();
            }

            Models.MicConfig config = new()
            {
                SampleRate = sampleRate,
                SampleWidth = sampleWidth,
                ChannelCount = channelCount
            };
            await _socket!.SendAsync(config);
        }
        catch
        {
            _logger.LogInformation("Mic connection closed");
            _cancellationToken = null;
            _cancelCallback?.Invoke();
            _cancelCallback = null;

            await _jsRuntime.InvokeVoidAsync("stopRecording");
            if (_socket != null)
            {
                await _socket.CloseAsync();
                _socket = null;
            }
        }
    }
}
