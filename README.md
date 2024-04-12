# MSD_P18538

Interactive Training Robot for Fire Safety


## How to setup a new RPi device

1. Use [RaspberryPi Imager](https://www.raspberrypi.com/software/) to create a loadable SD card. Choose the following options:
    - Device: Raspberry Pi 4
    - OS: Raspberry Pi OS (64-bit)
    - Device: SD Card
    - Next -> Edit Settings:
      - General:
        - Hostname: `msd-p18538`
        - Username: `pi`
        - Password: choose a secure password
      - Services:
        - Enable SSH
        - Use password authentication
2. Connect the RPi to a monitor, keyboard, and mouse.
3. Boot up the RPi and connect to the RIT Wi-Fi network.
4. Open a terminal window and run the following:

```sh
export GITHUB_LINK=https://raw.githubusercontent.com/BrianMonclus/MSD_P18538/main/software/setup.sh
curl $GITHUB_LINK | bash
```

## Requirements

- OpenAI account and API key
- RIT account to connect to Wi-Fi network
- Register Raspberry Pi to RIT network at start.rit.edu
  - Ensure hostname is `msd-p18538.[student.]rit.edu`
