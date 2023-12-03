using System.Runtime.CompilerServices;

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

    public async IAsyncEnumerable<string> GetTranscriptionStreamAsync([EnumeratorCancellation] CancellationToken cancellationToken)
    {
        var response = await _httpClient.GetStreamAsync(_route, cancellationToken);
        using var reader = new StreamReader(response);

        while (!reader.EndOfStream && !cancellationToken.IsCancellationRequested)
        {
            var line = await reader.ReadLineAsync();
            if (!string.IsNullOrEmpty(line))
            {
                yield return line;
            }
        }
    }


    public async Task StopTranscriptionAsync()
    {
        Console.WriteLine("Transcription stopped");
        var response = await _httpClient.DeleteAsync(_route);
        response.EnsureSuccessStatusCode();
    }
}
