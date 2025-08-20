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
    static const uint32_t ROW_COUNT = 26;
    static const uint32_t COL_COUNT = 39;
    static const uint32_t BCD_FRAME_COUNT = 14;
    static const uint32_t BCD_FRAME_BYTES = 48;   // 2 + 39 + 4 + 3
    static const uint32_t ROW_BYTES = BCD_FRAME_COUNT * BCD_FRAME_BYTES;
    static const uint32_t BITSTREAM_LENGTH = (ROW_COUNT * ROW_BYTES);

  private:
    static PIO bitstream_pio;
    static uint bitstream_sm;
    static uint bitstream_sm_offset;

    uint16_t brightness = 256;

    // must be aligned for 32bit dma transfer
    alignas(4) uint8_t bitstream[BITSTREAM_LENGTH] = {0};
    const uint32_t bitstream_addr = (uint32_t)bitstream;
    static Blinky* blinky;
    static void dma_complete();


  public:
    ~Blinky();

    void init();
    static inline void pio_program_init(PIO pio, uint sm, uint offset);

    void clear();

    void update(PicoGraphics *graphics);

    void set_brightness(float value);
    float get_brightness();
    void adjust_brightness(float delta);

    void set_pixel(int x, int y, uint8_t v);

  private:
    void partial_teardown();
    void dma_safe_abort(uint channel);
  };

}