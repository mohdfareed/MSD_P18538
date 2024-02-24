# MSD_P18538

Interactive Training Robot for Fire Safety


## How to setup a new RPi device

1. Use [RaspberryPi Imager](https://www.raspberrypi.com/software/) to create a loadable SD card. Options include Raspbian OS, 64-bit
2. SSH into the device or open a terminal window on the device
3. Run the following to set up the device:

```sh
export GITHUB_TOKEN=<your github token>
export GITHUB_LINK=https://raw.githubusercontent.com/BrianMonclus/MSD_P18538/main/software/setup.sh
curl $GITHUB_LINK\?token=$GITHUB_TOKEN | bash
```
