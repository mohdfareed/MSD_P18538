using System.Text.Json.Serialization;

namespace Models;

public class MicConfig
{
    [JsonPropertyName("sample_rate")]
    public int SampleRate { get; set; }
}
