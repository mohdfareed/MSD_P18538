using System.Net.WebSockets;
using System.Text;
using System.Text.Json;

namespace Services;

public class WebSocketConnection : IDisposable
{
    private readonly ClientWebSocket _socket = new();

    public async Task ConnectAsync(string url,
    CancellationToken cancellationToken = default)
    {
        try
        {
            await _socket.ConnectAsync(new Uri(url), cancellationToken);
        }
        catch (WebSocketException)
        {
            await CloseAsync(cancellationToken);
            throw;
        }
    }

    public async Task SendAsync<T>(T data,
    CancellationToken cancellationToken = default)
    {
        byte[] buffer;
        WebSocketMessageType messageType;

        switch (data)
        {
            case string str:
                buffer = Encoding.UTF8.GetBytes(str);
                messageType = WebSocketMessageType.Text;
                break;
            case byte[] bytes:
                buffer = bytes;
                messageType = WebSocketMessageType.Binary;
                break;
            default:
                var json_data = JsonSerializer.Serialize(data);
                buffer = Encoding.UTF8.GetBytes(json_data);
                messageType = WebSocketMessageType.Text;
                break;
        }

        try
        {
            if (_socket.State != WebSocketState.Open)
            {
                throw new WebSocketException("Connection is not open");
            }
            await _socket.SendAsync(new ArraySegment<byte>(buffer),
            messageType, true, cancellationToken);
        }
        catch (WebSocketException)
        {
            await CloseAsync(cancellationToken);
            throw;
        }
    }


    public async Task<T?> ReceiveAsync<T>(
        CancellationToken cancellationToken = default)
    {
        try
        {
            var buffer = new byte[1024 * 4];
            using var ms = new MemoryStream();
            WebSocketReceiveResult result;
            if (_socket.State != WebSocketState.Open)
            {
                throw new WebSocketException("Connection is not open");
            }

            do
            {
                var arr = new ArraySegment<byte>(buffer);
                result = await _socket.ReceiveAsync(arr, cancellationToken);
                ms.Write(buffer, 0, result.Count);
            } while (!result.EndOfMessage);
            ms.Seek(0, SeekOrigin.Begin);

            if (result.MessageType == WebSocketMessageType.Close)
                return default;

            if (typeof(T) == typeof(byte[]))
            {
                if (result.MessageType != WebSocketMessageType.Binary)
                {
                    throw new InvalidOperationException(
                        "Expected binary message");
                }
                return (T)(object)ms.ToArray();
            }
            else if (typeof(T) == typeof(string))
            {
                if (result.MessageType != WebSocketMessageType.Text)
                {
                    throw new InvalidOperationException(
                        "Expected text message");
                }
                return (T)(object)Encoding.UTF8.GetString(ms.ToArray());
            }
            else
            {
                if (result.MessageType != WebSocketMessageType.Text)
                {
                    throw new InvalidOperationException(
                        "Expected text message for JSON deserialization");
                }
                string text = Encoding.UTF8.GetString(ms.ToArray());
                return JsonSerializer.Deserialize<T>(text);
            }
        }
        catch (WebSocketException)
        {
            await CloseAsync(cancellationToken);
            throw;
        }
    }

    public async Task CloseAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            await _socket.CloseAsync(WebSocketCloseStatus.NormalClosure,
            "Closing", cancellationToken);
        }
        catch { } // Ignore closing errors
        finally
        {
            Dispose();
        }
    }

    public void Dispose()
    {
        _socket.Abort();
        _socket.Dispose();
        GC.SuppressFinalize(this);
    }
}
