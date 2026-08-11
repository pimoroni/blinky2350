#pragma once

#include "hardware/pio.h"
#include "pico_graphics.hpp"
#include "common/pimoroni_common.hpp"

namespace pimoroni {

  class Blinky {
  public:
    // physical LED matrix dimensions
    static const int WIDTH  = 39;
    static const int HEIGHT = 26;

    // largest supersample factor; the framebuffer is sized for this and
    // update() box-downsamples each factor*factor block to one physical pixel
    static const int MAX_SUPERSAMPLE = 4;

    // pin assignments
    static const uint8_t COLUMN_CLOCK           = 16;
    static const uint8_t COLUMN_DATA            = 17;
    static const uint8_t COLUMN_LATCH           = 18;
    static const uint8_t COLUMN_BLANK           = 19;

    static const uint8_t ROW_DATA               = 20;
    static const uint8_t ROW_DATA_CLOCK         = 21;

  private:
    static const uint32_t VBLANK_ROWS           = 5;
    static const uint32_t ROW_COUNT = HEIGHT + VBLANK_ROWS;
    static const uint32_t COL_COUNT = WIDTH;
    static const uint32_t BCD_FRAME_COUNT = 14;
    static const uint32_t BCD_FRAME_BYTES = 48;   // 2 + 39 + 4 + 3
    static const uint32_t ROW_BYTES = BCD_FRAME_COUNT * BCD_FRAME_BYTES;
    static const uint32_t BITSTREAM_LENGTH = (ROW_COUNT * ROW_BYTES);

  private:
    static PIO bitstream_pio;
    static uint bitstream_sm;
    static uint bitstream_sm_offset;

    uint16_t brightness = 128;

    // supersample factor (1, 2 or 4); the logical framebuffer is
    // WIDTH*supersample x HEIGHT*supersample
    int supersample = 1;

    // DMA source for the LED-matrix refresh. It is streamed continuously by DMA,
    // so it MUST live in SRAM: if it lands in PSRAM (e.g. via the GC heap) the
    // constant refresh reads contend with USB/XIP on the QSPI bus and throttle
    // the whole system. Static (not a per-object member) so it stays out of the
    // GC heap, and 32-bit aligned for DMA.
    alignas(4) static uint8_t bitstream[BITSTREAM_LENGTH];
    static uint32_t bitstream_addr;
    static Blinky* blinky;
    static void dma_complete();


  public:
    ~Blinky();

    void init();
    static inline void pio_program_init(PIO pio, uint sm, uint offset);

    void clear();

    void update();

    void set_brightness(float value);
    float get_brightness();
    void adjust_brightness(float delta);

    void set_supersample(int scale);
    int get_supersample();

    // current logical framebuffer dimensions (physical * supersample)
    int get_width();
    int get_height();

    void set_pixel(int x, int y, uint8_t v);

    uint32_t* get_framebuffer();

  private:
    void partial_teardown();
    void dma_safe_abort(uint channel);
    template<int SS> void downsample();
  };

}