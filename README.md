# Interstate 75<!-- omit in toc -->

## Pico, Pico W and RP2350 powered HUB75 LED matrix drivers<!-- omit in toc -->

This repository is home to the MicroPython firmware and examples for
Interstate 75, Interstate 75 W (Pico W Aboard) and Interstate 75 W (RP2350).

- [Get Interstate 75](#get-interstate-75)
- [Download Firmware](#download-firmware)
- [Installation](#installation)
  - [Interstate 75 W (RP2350)](#interstate-75-w-rp2350)
  - [Interstate 75 W (RP2040/Pico W Aboard)](#interstate-75-w-rp2040pico-w-aboard)
  - [Interstate 75](#interstate-75-1)
- [Useful Links](#useful-links)
- [Other Resources](#other-resources)

## Get Interstate 75

* [Interstate 75 W](https://shop.pimoroni.com/products/interstate-75-w) (now with RP2350 and RM2 wireless module aboard!)
* [Interstate 75](https://shop.pimoroni.com/products/interstate-75)

## Download Firmware

You can find the latest firmware releases at [https://github.com/pimoroni/interstate75/releases/latest](https://github.com/pimoroni/interstate75/releases/latest).

For each board there are two choices, a regular build that just updates the firmware and a "-with-examples" build which includes everything in [examples](examples) or [examples-2040](examples-2040), depending on your board.

:warning: If you've changed any of the code on your board then back up before flashing "-with-examples" - *your files will be erased!*

## Installation

### Interstate 75 W (RP2350)

1. Connect Interstate 75 W to your computer with a USB-C cable.
2. Put your device into bootloader mode by holding down the BOOT button whilst tapping RST.
3. Drag and drop the downloaded .uf2 file to the "RP2350" drive that appears.
4. Your device should reset, and you should then be able to connect to it using [Thonny](https://thonny.org/).

### Interstate 75 W (RP2040/Pico W Aboard)

1. Connect Interstate 75 W to your computer with a micro USB cable.
2. Put your device into bootloader mode by holding down the BOOTSEL button (on the Pico W) whilst tapping RST (on the Interstate 75 W board).
3. Drag and drop the downloaded .uf2 file to the "RPI-RP2" drive that appears.
4. Your device should reset, and you should then be able to connect to it using [Thonny](https://thonny.org/).

### Interstate 75

1. Connect Interstate 75 to your computer with a USB-C cable.
2. Put your device into bootloader mode by holding down the BOOT button whilst tapping RST.
3. Drag and drop the downloaded .uf2 file to the "RPI-RP2" drive that appears.
4. Your device should reset, and you should then be able to connect to it using [Thonny](https://thonny.org/).

## Useful Links

* [Function Reference](docs/README.md)
* [Learn: Getting Started with Interstate 75](https://learn.pimoroni.com/article/getting-started-with-interstate-75)
* [Learn: Displaying Animated GIFs on Interstate 75 W](https://learn.pimoroni.com/article/gifs-and-interstate-75-w)

## Other Resources

Links to community projects and other resources that you might find helpful can be found below. Note that these code examples have not been written/tested by us and we're not able to offer support with them.

* [Make a Scrolling Hub75 Matrix Display using a Pimoroni Interstate75W and MQTT](https://www.digitalurban.org/blog/2024/07/12/creating-an-scrolling-hub75-matrix-display-with-pimoroni-interstate75w-and-mqtt/)

