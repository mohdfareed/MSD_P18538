using System.Text.Json.Serialization;

namespace Models;

public class MicConfig
{
    [JsonPropertyName("sample_rate")]
    public int SampleRate { get; set; }

    [JsonPropertyName("sample_width")]
    public int SampleWidth { get; set; }

    [JsonPropertyName("num_channels")]
    public int NumChannels { get; set; }

    [JsonPropertyName("chunk_size")]
    public int ChunkSize { get; set; }
}
