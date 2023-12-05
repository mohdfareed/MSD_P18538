using System.Text;
using Microsoft.AspNetCore.Components.WebAssembly.Http;

namespace Services;

public class TranscriptionService
{
    private readonly HttpClient _httpClient;
    private readonly string _route;

    public TranscriptionService(HttpClient httpClient, Models.GlobalSettings globalSettings)
    {
        _httpClient = httpClient;
        _route = globalSettings.BackendBaseAddress + "/transcription/";
    }

    public async IAsyncEnumerable<string> GetTranscriptionStreamAsync()
    {
        // Configure the request
        using var request = new HttpRequestMessage(HttpMethod.Get, _route);
        request.SetBrowserResponseStreamingEnabled(true);

        // Send the request and get the response
        using var response = await _httpClient.SendAsync(request,
        HttpCompletionOption.ResponseHeadersRead);
        response.EnsureSuccessStatusCode();
        using var stream = await response.Content.ReadAsStreamAsync();

        // Read the response line by line
        var bytes = new byte[1024]; // max line length
        var bytesCount = 0;
        while ((bytesCount = await stream.ReadAsync(bytes)) > 0)
        {
            yield return Encoding.UTF8.GetString(bytes, 0, bytesCount);
            await Task.Delay(1); // delay to avoid blocking the UI
        }
    }

    public async Task StopTranscriptionAsync(CancellationToken cancellationToken = default)
    {
        await _httpClient.DeleteAsync(_route, cancellationToken);
    }
}
