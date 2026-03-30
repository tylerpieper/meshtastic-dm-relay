# Meshtastic DM Relay Overlay

This repository provides an automated build system to compile custom Meshtastic firmware with the `DMRelayModule`. 

Instead of maintaining a massive fork of all of Meshtastic, this repository acts as an "overlay". The build script will automatically:
1. Clone the pristine upstream Meshtastic firmare.
2. Check out the specific channel (branch or tag) you want.
3. Overlay our custom modules into the firmware source.
4. Patch the necessary core files strictly to register our module.
5. Compile the firmware using PlatformIO.

## Prerequisites
- **Python 3**
- Ensure PlatformIO is installed globally or available in your path (`pip install platformio`)

## Building

Run the python build script to generate the firmware:

```bash
python build.py --branch master --channel 0
```

### Options:
- `--branch`: The branch or tag of the Meshtastic firmware you want to build against. Default is `master`. Example: `v2.4.0`
- `--channel`: The LoRa channel to relay DMs to. Default is `0`. Example: `3`

Once complete, the compiled binary will be located inside `firmware/.pio/build/tbeam/firmware.bin`.
