# Control Software

This program is responsible for controlling the robot. It is written in Python
and is designed to run on a Raspberry Pi 4.

## Requirements

- [Python >=3.11](https://www.python.org/downloads/release/python-370/)

## Development Setup

```bash
./setup.sh
source .venv/bin/activate
```

## Design

```mermaid
classDiagram
    class main {
        +main()
    }

    class RobotPackage {
        <<package>> robot
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
        +recordings Queue[AudioData]
        +source Microphone
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
