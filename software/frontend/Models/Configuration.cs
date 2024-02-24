using System.Text.Json.Serialization;

namespace Models;

public class Config
{
    [JsonPropertyName("transcription_engine")]
    public string TranscriptionEngine { get; set; } = null!;
}
