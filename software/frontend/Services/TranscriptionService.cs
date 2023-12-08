using System.Net.WebSockets;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using Microsoft.JSInterop;

namespace Services;

public class TranscriptionService
{
    const string _route = "/transcription/"; // API route

    // javascript interop
    private readonly IJSRuntime _jsRuntime;
    private readonly DotNetObjectReference<TranscriptionService> _objRef;

    // routes
    private readonly HttpClient _httpClient; // used to call API
    private readonly string _http_route; // API http route
    private readonly string _websocket_route; // websocket route

    // audio socket
    private ClientWebSocket? _audioSocket;
    private Action? _cancellationAction;



    public TranscriptionService(HttpClient httpClient, Models.GlobalSettings globalSettings, IJSRuntime JSRuntime)
    {
        _httpClient = httpClient;
        _http_route = globalSettings.BackendHTTPUrl + _route;
        _websocket_route = globalSettings.BackendWSUrl + _route;

        _jsRuntime = JSRuntime;
        _objRef = DotNetObjectReference.Create(this);
    }

    public async IAsyncEnumerable<string> ReceiveTextStreamAsync(
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var buffer = new byte[1024];
        var textSocket = new ClientWebSocket();
        cancellationToken.Register(async () => { await CleanupAsync(textSocket); });
        await textSocket.ConnectAsync(new Uri(_websocket_route + "stream"), cancellationToken);

        while (textSocket.State == WebSocketState.Open)
        {
            var result = await textSocket.ReceiveAsync(buffer, cancellationToken);
            if (result.MessageType == WebSocketMessageType.Close) break;
            yield return Encoding.UTF8.GetString(buffer, 0, result.Count);
        }
    }

    public async Task StartAudioStreamingAsync(Action cancellationAction, CancellationToken cancellationToken = default)
    {
        _audioSocket = new ClientWebSocket();
        _cancellationAction = cancellationAction;

        cancellationToken.Register(async () =>
        {
            await _jsRuntime.InvokeVoidAsync("stopRecording");
            await CleanupAsync(_audioSocket);
        });

        await _audioSocket.ConnectAsync(new Uri(_websocket_route + "start"), cancellationToken);
        await _jsRuntime.InvokeVoidAsync("startRecording", _objRef, "AudioCaptureCallback", "AudioConfigCallback");
    }

    [JSInvokable]
    public async Task AudioCaptureCallback(byte[] audioData)
    {
        try
        {
            await _audioSocket!.SendAsync(
                audioData, WebSocketMessageType.Binary, true, default
            );  // send audio data to server
        }
        catch
        {
            _cancellationAction?.Invoke();
        }
    }

    [JSInvokable]
    public async Task AudioConfigCallback(Dictionary<string, object> config)
    {
        // config is a dictionary of MediaTrackSettings:
        //https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackSettings
        try
        {
            Models.MicConfig micConfig = new()
            {
                SampleRate = (int)config["sampleRate"]
            };
            await _audioSocket!.SendAsync(
                Encoding.UTF8.GetBytes(JsonSerializer.Serialize(micConfig)),
                WebSocketMessageType.Text, true, default
            ); // send configuration to server
        }
        catch
        {
            _cancellationAction?.Invoke();
        }
    }

    private static async Task CleanupAsync(ClientWebSocket socket)
    {
        try
        {
            await socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Cancelled", default);
        }
        catch (WebSocketException)
        {
            socket.Abort();
        }
        finally
        {
            socket.Dispose();
        }
    }
}
