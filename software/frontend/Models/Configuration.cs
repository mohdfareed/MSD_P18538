using System.Text.Json.Serialization;

namespace Models;

public class Config
{
    [JsonPropertyName("transcription_engine")]
    public string TranscriptionEngine { get; set; } = null!;
    public bool BluetoothOn { get; set; } = false;
    public bool AdhocOn { get; set; } = false;
}
