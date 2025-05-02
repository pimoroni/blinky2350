# Interstate75 (MicroPython) <!-- omit in toc -->

This library offers convenient functions for interacting with [Interstate75](https://shop.pimoroni.com/products/interstate-75) and [Interstate75W](https://shop.pimoroni.com/products/interstate-75-w) - Interstate75 and Interstate75W offer a convenient way and 2 input buttons for all your display and control needs.

- [Getting Started](#getting-started)
  - [Display Size](#display-size)
  - [Board Version](#board-version)
- [Advanced Configuration](#advanced-configuration)
  - [Colour Order](#colour-order)
  - [Panel Types](#panel-types)
  - [Strobe Invert](#strobe-invert)
- [Switches / Buttons](#switches--buttons)
- [RGB LED](#rgb-led)
- [Display](#display)

## Getting Started

The `Interstate75` class deals with RGB LED and buttons on the Interstate75 and 75W. To create one, import the `interstate75` module, then define a new `board` variable.


```python
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_32X32

i75 = Interstate75(display=DISPLAY_INTERSTATE75_32X32)
```

### Display Size

You can choose the HUB75 matrix display size by supplying `display=` as one of:

* `DISPLAY_INTERSTATE75_32X32`
* `DISPLAY_INTERSTATE75_64X32` - Two chained 32x32 or a single 64x32 panel
* `DISPLAY_INTERSTATE75_96X32` - Three chained 32x32 panels
* `DISPLAY_INTERSTATE75_96X48` - I have... no idea
* `DISPLAY_INTERSTATE75_128X32` - Four chained 32x32 panels
* `DISPLAY_INTERSTATE75_64X64`
* `DISPLAY_INTERSTATE75_128X64` - Two chained 64x64 or a single 128x64 panel
* `DISPLAY_INTERSTATE75_192X64` - Three chained 64x64 panels
* `DISPLAY_INTERSTATE75_256X64` - Four chained 64x64 or two 128x64 panels
* `DISPLAY_INTERSTATE75_128X128` - Two chained 128x64 panels arranged vertically

Some of these display sizes represent multiple panels in a horizontally chained configuration. Vertical mapping is unsupported with the exception of 128x128 which
has a special case. It's on our TODO list to make this better... somehow!

### Board Version

On RP2040 variants the version of Interstate75 you're using should be automatically detected. Check `i75.interstate75w` to verify this. It should be `True` on a W and `False` on a non-W.

The RP2350 has only one variant, and `i75.interstate75w` does not exist.

## Advanced Configuration

There are some additional options for the `Interstate75` class, outlined below.

### Colour Order

If you've got funky colours or wrong rainbows you might need to adjust your panel colour order. By default we use RGB (Red, Green, Blue). Supply `color_order=` as one of:

* `COLOR_ORDER_RGB`
* `COLOR_ORDER_RBG`
* `COLOR_ORDER_GRB`
* `COLOR_ORDER_GBR`
* `COLOR_ORDER_BRG`
* `COLOR_ORDER_BGR`

### Panel Types

There are to panel types, supplied with `panel_type`:

* `PANEL_GENERIC` - the default panel configuration
* `PANEL_FM6126A` - sends special `FM6126A` config magic on startup

### Strobe Invert

If your panel strobe pin logic is inverted, specify `stb_invert=True`

## Switches / Buttons

Interstate75 and 75W have two buttons in the front of the board. To read one of the switches, call `.switch_pressed(switch)`, where `switch` is a value from `0` to `.NUM_SWITCHES - 1`. This returns `True` when the specified switch is pressed, and `False` otherwise.

To read a specific input, the `interstate75` module contains these handy constants:

* `SWITCH_A` = `0`
* `SWITCH_B` = `1`

Interstate75 (non W) uses the boot button instead of `SWITCH_B`:

* `SWITCH_A` = `0`
* `SWITCH_BOOT` = `1`

Interstate75 W (RP2350) has a boot button in addition to the switches:

* `SWITCH_A` = `0`
* `SWITCH_B` = `1`
* `SWITCH_BOOT` = `2`

```python
if board.switch_pressed(SWITCH_A):
    # Do something interesting here!

# Either for Interstate 75W
if board.switch_pressed(SWITCH_B):
    # Do something else even more interesting here!

# Or for Interstate 75 / or 75W RP2350
if board.switch_pressed(SWITCH_BOOT):
    # Do something else even more interesting here!
```

## RGB LED

Interstate 75 has an RGB LED. You can set its colour with:

`.set_led(r, g, b)`

Where r, g, b are values between 0 and 255:

```python
board.set_led(255, 0, 0)  # Makes the LED Red
board.set_led(0, 255, 0)  # Makes the LED Blue
board.set_led(0, 0, 255)  # Makes the LED Green
```

## Display

The display is all handled by our custom PicoGraphics drivers they can be accessed via `.display`:

```python
display = i75.display

display.text("Hello World!", 0, 0)
display.line(0, 0, 128, 64) 
i75.update()  # Update the display
```

For a detailed PicoGraphics guide, see: [https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/picographics](https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/modules/picographics)