using System.Text.Json.Serialization;

namespace Models;

public class Config
{
    [JsonPropertyName("transcription_engine")]
    public string TranscriptionEngine { get; set; } = null!;

    [JsonPropertyName("openai_api_key")]
    public string OpenaiApiKey { get; set; } = null!;
}
