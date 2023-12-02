# Backend

## Overview

The backend is responsible for controlling the robot and the Raspberry Pi. It consists of different endpoints that are exposed locally. The endpoints are used by the frontend to control the robot and the Raspberry Pi.

## Requirements

- [Python >=3.11](https://www.python.org/downloads/release/python-370/)

## Development Setup

```sh
./setup.sh
source venv/bin/activate
./startup.py --debug
```

## Design

```mermaid
classDiagram
    class ControlPackage {
        <<package>>
    }
    class main {
        +main()
    }

    class RobotPackage {
        <<package>>
    }
    class Motor {
        +move(speed)
    }
    class Servo {
        +steer(angle)
    }
    class Speaker {
        +play(filename)
    }

    class ControllerPackage {
        <<package>>
    }
    class BluetoothController {
        +connect()
        +disconnect()
        +start(config)
        +stop()
    }

    class AudioPackage {
        <<package>>
    }
    class Transcription {
        +transcriber Recognizer
        +transcribe(Queue recordings)
    }
    class Core {
        +recordings Queue[AudioData]
        +source Microphone
        +startup()
        +record()
    }

    ControlPackage --> main : contains
    main --> RobotPackage : uses
    main --> ControllerPackage : uses
    main --> AudioPackage : uses
    RobotPackage --> Motor : contains
    RobotPackage --> Servo : contains
    RobotPackage --> Speaker : contains
    ControllerPackage --> BluetoothController : contains
    AudioPackage --> Transcription : contains
    AudioPackage --> Core : contains
```

### Live Transcription

```mermaid
flowchart LR
    subgraph Recording ["Recording Thread"]
    rec{{"Recorder"}}
    end

    subgraph Transcription ["Transcription Thread"]
    transcriber{{"Transcriber"}}
    end

    subgraph API ["Speech-to-Text API"]
    api1("Google Cloud API")
    api2("Microsoft Azure API")
    end

    subgraph Output ["Output"]
    output_logic{{"Logic"}}
    end

    source(("Audio Source")) --> rec
    rec -->|audio chunks| queue[("Audio Queue")]
    transcriber -->|pulls recordings| queue[("Audio Queue")]
    transcriber <--> API
    transcriber -->|emits transcriptions| output_logic
    output_logic -->|feeds| display(("Display\n(Console)"))
```

#### Audio Recording

```mermaid
flowchart LR
    subgraph Recording ["Recording Thread"]
        rec{{"Recorder"}} -->|data| test{"Is audio at threshold?"}
        test -->|yes| start[["Record audio"]]
        start -->|audio data| rec
        test -->|no| rec
    end

    source(("Audio Source")) --> rec
    rec -->|audio chunks| queue[("Audio Queue")]
```

#### Transcription

```mermaid
flowchart LR
    subgraph Transcription ["Transcription Thread"]
        transcriber{{"Transcriber"}} <-->|phrases| tracker[[Phrase Detection]]
        tracker <-->|tracks phrase| buffer[("Buffer\n(Temp Storage)")]

        tracker -->|tracks pause length| detector{"Is phrase\ncomplete?"}
        detector -->|yes| complete[["Emit\nPhrase Terminator"]]
        detector -->|yes| erase[["Erase Buffer"]]
        erase --> buffer
    end

    subgraph API ["Speech-to-Text API"]
        api1("Google Cloud API")
        api2("Microsoft Azure API")
    end

    subgraph Output ["Output"]
        output_logic{{"Logic"}}
    end

    API <-->|Transcriptions| transcriber
    transcriber -->|text stream| output_logic
    transcriber -->|pulls recordings| queue[("Audio Queue")]
    complete -->|terminator| output_logic
```

#### Output

```mermaid
flowchart LR
    subgraph Output ["Output"]
        output_logic{{"Logic"}}
        output_logic --> test{"Is phrase\nterminator received?"}
        test -->|yes| new[["Start\nNew Phrase"]]
        output_logic --> overwrite[["Overwrite Phrase"]]
    end

    subgraph Transcription ["Transcription Thread"]
        transcriber{{"Transcriber"}}
    end

    transcriber -->|text stream| output_logic
    new -->|new line| display(("Display\n(Console)"))
    overwrite -->|overwrite line| display
```



**Transcription process:**

1. **Audio Source**: An audio receiver or microphone continuously captures audio.
2. **Recording Device**: It listens to the audio source in the background and stores recordings.
3. **Queue of Recordings**: A queue that holds all the audio recordings to be processed, operating in a different thread from the main application.
4. **Transcriber**: This component continuously transcribes the recordings from the queue.
5. **Temporary File (Buffer)**: A buffer that accumulates audio data, waiting for pauses that signal the end of phrases.
6. **Phrase Detection**: Within the transcriber, phrase detection logic determines when a phrase is complete based on pauses in speech.
7. **Ongoing Transcription**: The transcriber continuously transcribes the audio, allowing for self-correction as new audio data is received.
8. **Phrase Output**: Once a phrase is locked-in, it's emitted separately from the ongoing transcription.
9. **Console Output**: The last transcription is continuously overwritten until a phrase separator is emitted, at which point a new line is started for a new phrase on the console.
