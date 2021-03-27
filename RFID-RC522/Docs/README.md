# Enable SPI on Raspbery Pi
````
sudo raspi-config
````

Go to `5 Interfacing Options`, `P4 SPI`, and enable it

# Package Dependencies
````
sudo pip3 install spidev
sudo pip3 install mfrc522
````

# Wiring
- SDA connects to Pin 24.
- SCK connects to Pin 23.
- MOSI connects to Pin 19.
- MISO connects to Pin 21.
- GND connects to Pin 6.
- RST connects to Pin 22.
- 3.3v connects to Pin 1.

#Credit to

https://pimylifeup.com/raspberry-pi-rfid-rc522/
