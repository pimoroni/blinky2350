#pragma once

#include "hardware/pio.h"
#include "pico_graphics.hpp"
#include "common/pimoroni_common.hpp"

namespace pimoroni {

  class Blinky {
  public:
    static const int WIDTH  = 39;
    static const int HEIGHT = 26;

    // pin assignments
    static const uint8_t COLUMN_CLOCK           = 16;
    static const uint8_t COLUMN_DATA            = 17;
    static const uint8_t COLUMN_LATCH           = 18;
    static const uint8_t COLUMN_BLANK           = 19;

    static const uint8_t ROW_DATA               = 20;
    static const uint8_t ROW_DATA_CLOCK         = 21;

  private:
    static const uint32_t VBLANK_ROWS           = 5;
    static const uint32_t ROW_COUNT = HEIGHT + VBLANK_ROWS;   // 31 scanned rows
    static const uint32_t BCD_FRAME_COUNT = 14;               // 14-bit BCD PWM
    // One bit-plane is WIDTH column bits padded up to a 2-word (64-bit) boundary
    // so the data state machine keeps planes word-aligned as it streams them.
    static const uint32_t PLANE_WORDS = 2;
    static const uint32_t PLANES_LENGTH = BCD_FRAME_COUNT * ROW_COUNT * PLANE_WORDS;

  private:
    static PIO pio;
    static uint data_sm;
    static uint ctrl_sm;
    static uint data_offset;
    static uint ctrl_offset;

    uint16_t brightness = 128;

    // DMA sources for the LED-matrix refresh. They are streamed continuously by
    // DMA, so they MUST live in SRAM: if they land in PSRAM (e.g. via the GC
    // heap) the constant refresh reads contend with USB/XIP on the QSPI bus and
    // throttle the whole system. Static (not per-object members) so they stay
    // out of the GC heap, and 32-bit aligned for DMA.
    //
    // Packed pixel planes, phase-major order [frame][row], streamed to the data
    // state machine.
    alignas(4) static uint32_t planes[PLANES_LENGTH];
    static uint32_t planes_addr;
    // BCD tick counts (2^frame), streamed one per phase to the ctrl SM.
    alignas(4) static uint32_t bcd_ticks[BCD_FRAME_COUNT];
    static uint32_t bcd_ticks_addr;
    static Blinky* blinky;


  public:
    ~Blinky();

    void init();
    static inline void pio_program_init(PIO pio, uint sm, uint offset);

    void clear();

    void update();

    void set_brightness(float value);
    float get_brightness();
    void adjust_brightness(float delta);

    void set_pixel(int x, int y, uint8_t v);

    uint32_t* get_framebuffer();

  private:
    void partial_teardown();
  };

}