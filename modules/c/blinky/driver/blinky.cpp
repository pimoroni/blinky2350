#include <math.h>

#include "hardware/dma.h"
#include "hardware/irq.h"
#include "hardware/clocks.h"


#ifndef NO_QSTR
#include "blinky.pio.h"
#endif

#include "blinky.hpp"

// Two PIO state machines refresh the panel with no CPU intervention between
// scanlines (see blinky.pio). The data SM shifts packed pixel planes into the
// column shift registers; the ctrl SM latches each plane, walks the row select,
// and times the BCD display period. Each SM is fed by its own DMA stream so no
// timing/pin control has to be duplicated into the pixel data.
//
// The pixel planes are packed one bit per column, WIDTH bits per plane padded to
// a 2-word boundary, in phase-major order: [frame][row][PLANE_WORDS].

static uint dma_pix;
static uint dma_pix_reload;
static uint dma_tick;
static uint dma_tick_reload;

namespace pimoroni {
  uint32_t __attribute__((section(".uninitialized_data"))) __attribute__ ((aligned (4))) framebuffer[Blinky::WIDTH * Blinky::HEIGHT];

  // DMA sources, kept in SRAM (.bss), zero-initialised, 32-bit aligned. See blinky.hpp.
  alignas(4) uint32_t Blinky::planes[Blinky::PLANES_LENGTH];
  uint32_t Blinky::planes_addr = (uint32_t)Blinky::planes;
  alignas(4) uint32_t Blinky::bcd_ticks[Blinky::BCD_FRAME_COUNT];
  uint32_t Blinky::bcd_ticks_addr = (uint32_t)Blinky::bcd_ticks;

  Blinky* Blinky::blinky = nullptr;
  PIO Blinky::pio = pio0;
  uint Blinky::data_sm = 0;
  uint Blinky::ctrl_sm = 0;
  uint Blinky::data_offset = 0;
  uint Blinky::ctrl_offset = 0;

  Blinky::~Blinky() {
    if(blinky == this) {
      partial_teardown();

      dma_channel_unclaim(dma_pix_reload);
      dma_channel_unclaim(dma_pix);
      dma_channel_unclaim(dma_tick_reload);
      dma_channel_unclaim(dma_tick);
      pio_sm_unclaim(pio, data_sm);
      pio_sm_unclaim(pio, ctrl_sm);
      pio_remove_program(pio, &blinky_data_program, data_offset);
      pio_remove_program(pio, &blinky_ctrl_program, ctrl_offset);

      blinky = nullptr;
    }
  }

  void Blinky::partial_teardown() {
    // Stop both state machines
    pio_sm_set_enabled(pio, data_sm, false);
    pio_sm_set_enabled(pio, ctrl_sm, false);

    // Make sure the display is off by turning off the column drivers
    const uint pins_to_set = 1 << COLUMN_BLANK;
    pio_sm_set_pins_with_mask(pio, ctrl_sm, pins_to_set, pins_to_set);

    // Clock out data to turn off the row drivers
    gpio_put(ROW_DATA, false);
    for(uint32_t i = 0; i < ROW_COUNT; i++) {
      sleep_us(10);
      gpio_put(ROW_DATA_CLOCK, true);
      sleep_us(10);
      gpio_put(ROW_DATA_CLOCK, false);
    }

    // Break each channel's chain (point it at itself) so aborting can't restart it
    const uint channels[] = {dma_pix, dma_pix_reload, dma_tick, dma_tick_reload};
    for(uint ch : channels) {
      dma_hw->ch[ch].al1_ctrl = (dma_hw->ch[ch].al1_ctrl & ~DMA_CH0_CTRL_TRIG_CHAIN_TO_BITS) | (ch << DMA_CH0_CTRL_TRIG_CHAIN_TO_LSB);
    }
    // Abort any in-progress DMA transfers. dma_channel_abort polls the BUSY bit
    // to fence off in-flight transfers; no DMA completion IRQs are enabled here.
    dma_channel_abort(dma_pix_reload);
    dma_channel_abort(dma_pix);
    dma_channel_abort(dma_tick_reload);
    dma_channel_abort(dma_tick);
  }

  void Blinky::init() {

    if(blinky != nullptr) {
      // Tear down the old instance's hardware resources
      partial_teardown();
    }

    // BCD tick counts: plane p is lit for 2^p ticks (binary-weighted PWM).
    for(uint8_t frame = 0; frame < BCD_FRAME_COUNT; frame++) {
      bcd_ticks[frame] = 1u << frame;
    }
    // Start every plane clear. Vblank rows (y >= HEIGHT) are never written by
    // set_pixel, so they stay dark and de-ghost the scan.
    for(uint32_t i = 0; i < PLANES_LENGTH; i++) {
      planes[i] = 0;
    }

    gpio_init(COLUMN_CLOCK); gpio_set_dir(COLUMN_CLOCK, GPIO_OUT); gpio_put(COLUMN_CLOCK, false);
    gpio_init(COLUMN_DATA); gpio_set_dir(COLUMN_DATA, GPIO_OUT); gpio_put(COLUMN_DATA, false);
    gpio_init(COLUMN_LATCH); gpio_set_dir(COLUMN_LATCH, GPIO_OUT); gpio_put(COLUMN_LATCH, false);
    gpio_init(COLUMN_BLANK); gpio_set_dir(COLUMN_BLANK, GPIO_OUT); gpio_put(COLUMN_BLANK, true);

    // initialise the row select, and set them to a non-visible row to avoid flashes during setup
    gpio_init(ROW_DATA); gpio_set_dir(ROW_DATA, GPIO_OUT); gpio_put(ROW_DATA, false);
    gpio_init(ROW_DATA_CLOCK); gpio_set_dir(ROW_DATA_CLOCK, GPIO_OUT); gpio_put(ROW_DATA_CLOCK, true);

    sleep_ms(100);

    // Clock out data to turn off the row drivers
    gpio_put(ROW_DATA, false);
    for(uint32_t i = 0; i < ROW_COUNT; i++) {
      sleep_us(10);
      gpio_put(ROW_DATA_CLOCK, true);
      sleep_us(10);
      gpio_put(ROW_DATA_CLOCK, false);
    }

    // configure full output current in register 2

    uint16_t reg1 = 0b1111111111001110;

    // clock the register value to the first 2 driver chips
    for(uint32_t j = 0; j < 2; j++) {
      for(uint32_t i = 0; i < 16; i++) {
        if(reg1 & (1U << (16 - 1 - i))) {
          gpio_put(COLUMN_DATA, true);
        }else{
          gpio_put(COLUMN_DATA, false);
        }
        sleep_us(10);
        gpio_put(COLUMN_CLOCK, true);
        sleep_us(10);
        gpio_put(COLUMN_CLOCK, false);
      }
    }

    // clock the last chip and latch the value
    for(uint32_t i = 0; i < 16; i++) {
      if(reg1 & (1U << (16 - 1 - i))) {
        gpio_put(COLUMN_DATA, true);
      }else{
        gpio_put(COLUMN_DATA, false);
      }

      sleep_us(10);
      gpio_put(COLUMN_CLOCK, true);
      sleep_us(10);
      gpio_put(COLUMN_CLOCK, false);

      if(i == 4) {
        gpio_put(COLUMN_LATCH, true);
      }
    }
    gpio_put(COLUMN_LATCH, false);

    // reapply the blank as the above seems to cause a slight glow.
    // Note, this will produce a brief flash if a visible row is selected (which it shouldn't be)
    gpio_put(COLUMN_BLANK, false);
    sleep_us(10);
    gpio_put(COLUMN_BLANK, true);

    // setup the pio if it has not previously been set up
    pio = pio0;
    if(blinky == nullptr) {
      data_sm = pio_claim_unused_sm(pio, true);
      ctrl_sm = pio_claim_unused_sm(pio, true);
      data_offset = pio_add_program(pio, &blinky_data_program);
      ctrl_offset = pio_add_program(pio, &blinky_ctrl_program);
    }

    pio_gpio_init(pio, COLUMN_CLOCK);
    pio_gpio_init(pio, COLUMN_DATA);
    pio_gpio_init(pio, COLUMN_LATCH);
    pio_gpio_init(pio, COLUMN_BLANK);
    pio_gpio_init(pio, ROW_DATA);
    pio_gpio_init(pio, ROW_DATA_CLOCK);

    // Hold the column blank high before enabling outputs to avoid a momentary flash
    const uint pins_to_set = 1 << COLUMN_BLANK;
    pio_sm_set_pins_with_mask(pio, ctrl_sm, pins_to_set, pins_to_set);

    // pin directions: the data SM drives the column clock and data; the ctrl SM
    // drives the column latch/blank and the row data/clock
    pio_sm_set_consecutive_pindirs(pio, data_sm, COLUMN_CLOCK, 2, true);   // 16, 17
    pio_sm_set_consecutive_pindirs(pio, ctrl_sm, COLUMN_LATCH, 4, true);   // 18, 19, 20, 21

    // Pin both SMs to a fixed 150MHz so the scan-out timing (bit clock, BCD PWM,
    // row blanking) is independent of clk_sys. 150MHz is the rate the panel was
    // designed and validated at.
    float div = (float)clock_get_hz(clk_sys) / 150000000.0f;

    // data SM: shifts column data out, clocked by sideset column clock
    pio_sm_config dc = blinky_data_program_get_default_config(data_offset);
    sm_config_set_sideset_pins(&dc, COLUMN_CLOCK);
    sm_config_set_out_pins(&dc, COLUMN_DATA, 1);
    sm_config_set_out_shift(&dc, true, true, 32);       // shift right, autopull, threshold 32
    sm_config_set_fifo_join(&dc, PIO_FIFO_JOIN_TX);
    sm_config_set_clkdiv(&dc, div);
    pio_sm_init(pio, data_sm, data_offset, &dc);

    // Preload Y with the per-plane column count (WIDTH - 1); set's 5-bit
    // immediate can't reach it, so the data SM copies Y to X each plane.
    pio_sm_put_blocking(pio, data_sm, WIDTH - 1);
    pio_sm_exec(pio, data_sm, pio_encode_pull(false, true));
    pio_sm_exec(pio, data_sm, pio_encode_out(pio_y, 32));

    // ctrl SM: latch/blank, row select walk, BCD timing
    pio_sm_config cc = blinky_ctrl_program_get_default_config(ctrl_offset);
    sm_config_set_set_pins(&cc, COLUMN_LATCH, 4);
    sm_config_set_out_shift(&cc, true, false, 32);      // shift right, no autopull (explicit pull)
    sm_config_set_fifo_join(&cc, PIO_FIFO_JOIN_TX);
    sm_config_set_clkdiv(&cc, div);
    pio_sm_init(pio, ctrl_sm, ctrl_offset, &cc);

    // DMA: pixel planes -> data SM, tick counts -> ctrl SM. Each stream has a
    // reload channel that rewrites the data channel's read address on wrap, so
    // both refresh forever with no CPU involvement.
    planes_addr = (uint32_t)planes;
    bcd_ticks_addr = (uint32_t)bcd_ticks;

    if(blinky == nullptr) {
      dma_pix = dma_claim_unused_channel(true);
      dma_pix_reload = dma_claim_unused_channel(true);
      dma_tick = dma_claim_unused_channel(true);
      dma_tick_reload = dma_claim_unused_channel(true);
    }

    dma_channel_config pc = dma_channel_get_default_config(dma_pix);
    channel_config_set_transfer_data_size(&pc, DMA_SIZE_32);
    channel_config_set_dreq(&pc, pio_get_dreq(pio, data_sm, true));
    channel_config_set_chain_to(&pc, dma_pix_reload);
    dma_channel_configure(dma_pix, &pc, &pio->txf[data_sm], planes, PLANES_LENGTH, false);

    dma_channel_config prc = dma_channel_get_default_config(dma_pix_reload);
    channel_config_set_transfer_data_size(&prc, DMA_SIZE_32);
    channel_config_set_read_increment(&prc, false);
    channel_config_set_write_increment(&prc, false);
    channel_config_set_chain_to(&prc, dma_pix);
    dma_channel_configure(dma_pix_reload, &prc, &dma_hw->ch[dma_pix].read_addr, &planes_addr, 1, false);

    dma_channel_config tc = dma_channel_get_default_config(dma_tick);
    channel_config_set_transfer_data_size(&tc, DMA_SIZE_32);
    channel_config_set_dreq(&tc, pio_get_dreq(pio, ctrl_sm, true));
    channel_config_set_chain_to(&tc, dma_tick_reload);
    dma_channel_configure(dma_tick, &tc, &pio->txf[ctrl_sm], bcd_ticks, BCD_FRAME_COUNT, false);

    dma_channel_config trc = dma_channel_get_default_config(dma_tick_reload);
    channel_config_set_transfer_data_size(&trc, DMA_SIZE_32);
    channel_config_set_read_increment(&trc, false);
    channel_config_set_write_increment(&trc, false);
    channel_config_set_chain_to(&trc, dma_tick);
    dma_channel_configure(dma_tick_reload, &trc, &dma_hw->ch[dma_tick].read_addr, &bcd_ticks_addr, 1, false);

    // Enable both SMs (they block on their FIFOs), then start both streams
    pio_sm_set_enabled(pio, data_sm, true);
    pio_sm_set_enabled(pio, ctrl_sm, true);
    dma_start_channel_mask((1u << dma_pix) | (1u << dma_tick));

    blinky = this;
  }

  void Blinky::clear() {
    if(blinky == this) {
      for(uint8_t y = 0; y < HEIGHT; y++) {
        for(uint8_t x = 0; x < WIDTH; x++) {
          set_pixel(x, y, 0);
        }
      }
    }
  }

  void Blinky::set_pixel(int x, int y, uint8_t v) {
    if(x < 0 || x >= WIDTH || y < 0 || y >= HEIGHT) return;

    // Column order into the shift chain. Verify orientation on hardware; if the
    // image is mirrored horizontally, drop this flip.
    uint32_t col = (WIDTH - 1) - x;
    uint32_t word = col >> 5;             // 0 for columns 0-31, 1 for 32-38
    uint32_t bit = col & 31;

    uint32_t gamma_v = (uint32_t)GAMMA_14BIT[v] * this->brightness;
    gamma_v >>= 8;

    // Scatter the 14 gamma bits across the 14 bit-planes for this row.
    for(uint8_t frame = 0; frame < BCD_FRAME_COUNT; frame++) {
      uint32_t *p = &planes[((frame * ROW_COUNT) + y) * PLANE_WORDS + word];
      if(gamma_v & 1) {
        *p |= (1u << bit);
      } else {
        *p &= ~(1u << bit);
      }
      gamma_v >>= 1;
    }
  }

  void Blinky::set_brightness(float value) {
    value = value < 0.0f ? 0.0f : value;
    value = value > 1.0f ? 1.0f : value;
    // Max brightness is - in fact - 256 since it's applied with:
    // result = (channel * brightness) >> 8
    // eg: (255 * 256) >> 8 == 255
    this->brightness = floorf(value * 256.0f);
  }

  float Blinky::get_brightness() {
    return this->brightness / 256.0f;
  }

  void Blinky::adjust_brightness(float delta) {
    this->set_brightness(this->get_brightness() + delta);
  }

  uint32_t* Blinky::get_framebuffer() {
    return framebuffer;
  }

  void Blinky::update() {
    if(blinky == this) {
      uint32_t *p = (uint32_t *)framebuffer;

      for(uint8_t y = 0; y < HEIGHT; y++) {
        for(uint8_t x = 0; x < WIDTH; x++) {
          uint32_t col = *p;
          uint8_t r = (col & 0xff0000) >> 16;
          uint8_t g = (col & 0x00ff00) >> 8;
          uint8_t b = (col & 0x0000ff) >> 0;

          // Approximate brightness of the colour, mapped to our mono display
          uint16_t brightness = ((r + g + b) * 255) / 765;
          set_pixel(x, y, brightness);
          p++;
        }
      }
    }
  }

}
