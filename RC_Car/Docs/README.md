# Remote Controlled Car

Camera and motion tracking features.

## Wiring
**GPIO pins for the left motors**
- GPIO 23 <-> Dark yellow wire
- GPIO 24 <-> Light yellow wire
- GPIO 18 <-> Black wire

**GPIO pins for the right motors**
- GPIO 13 <-> Green wire
- GPIO 6 <-> Blue wire
- GPIO 19 <-> Gray wire

**GPIO pins for the servo**
- GPIO 17 <-> yellow wire
- GPIO 27 <-> red wire
- GPIO 22 <-> brown wire

There is no code logic for the servo currently but it shouldn't be hard to make the camera move left and right someday.

Start the application by running
````
// server IP is specified in the script
run.sh
````

