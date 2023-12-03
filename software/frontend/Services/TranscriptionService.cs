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
        using var response = await _httpClient.GetStreamAsync(_route);
        using var reader = new StreamReader(response);
        while (!reader.EndOfStream)
        {
            Console.WriteLine("Reading line");
            var line = await reader.ReadLineAsync();
            if (!string.IsNullOrEmpty(line))
            {
                yield return line;
            }
        }

    }

    public async Task StopTranscriptionAsync()
    {
        var response = await _httpClient.DeleteAsync(_route);
        response.EnsureSuccessStatusCode();
    }
}
