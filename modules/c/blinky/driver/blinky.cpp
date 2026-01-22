#include <math.h>

#include "hardware/dma.h"
#include "hardware/irq.h"
#include "hardware/clocks.h"


#ifndef NO_QSTR
#include "blinky.pio.h"
#endif

#include "blinky.hpp"

// pixel data is stored as a stream of bits delivered in the
// order the PIO needs to manage the shift registers, row
// selects, delays, and latching/blanking
//
// the pins used are:
//
//  - 13: column clock (sideset)
//  - 14: column data  (out base)
//  - 15: column latch
//  - 16: column blank
//  - 17: row select bit 0
//  - 18: row select bit 1
//  - 19: row select bit 2
//  - 20: row select bit 3
//
// the framebuffer data is structured like this:
//
// for each row:
//   for each bcd frame:
//            0: 00111111                           // row pixel count (minus one)
//            1: xxxxrrrr                           // row select bits
//      2  - 27: xxxxxxxv, xxxxxxxv, xxxxxxxv, ...  // pixel data
//      66 - 67: xxxxxxxx, xxxxxxxx,                // dummy bytes to dword align
//      68 - 71: tttttttt, tttttttt, tttttttt       // bcd tick count (0-65536)
//
//  .. and back to the start

static uint32_t dma_channel;
static uint32_t dma_ctrl_channel;

namespace pimoroni {
  uint32_t __attribute__((section(".uninitialized_data"))) __attribute__ ((aligned (4))) framebuffer[Blinky::WIDTH * Blinky::HEIGHT];

  Blinky* Blinky::blinky = nullptr;
  PIO Blinky::bitstream_pio = pio0;
  uint Blinky::bitstream_sm = 0;
  uint Blinky::bitstream_sm_offset = 0;

  Blinky::~Blinky() {
    if(blinky == this) {
      partial_teardown();

      dma_channel_unclaim(dma_ctrl_channel); // This works now the teardown behaves correctly
      dma_channel_unclaim(dma_channel); // This works now the teardown behaves correctly
      pio_sm_unclaim(bitstream_pio, bitstream_sm);
      pio_remove_program(bitstream_pio, &blinky_program, bitstream_sm_offset);

      blinky = nullptr;
    }
  }

  void Blinky::partial_teardown() {
    // Stop the bitstream SM
    pio_sm_set_enabled(bitstream_pio, bitstream_sm, false);

    // Make sure the display is off by turning off the column drivers
    const uint pins_to_set = 1 << COLUMN_BLANK;
    pio_sm_set_pins_with_mask(bitstream_pio, bitstream_sm, pins_to_set, pins_to_set);

    // Clock out data to turn off the row drivers
    gpio_put(ROW_DATA, false);
    for(uint32_t i = 0; i < ROW_COUNT; i++) {
      sleep_us(10);
      gpio_put(ROW_DATA_CLOCK, true);
      sleep_us(10);
      gpio_put(ROW_DATA_CLOCK, false);
    }

    dma_hw->ch[dma_ctrl_channel].al1_ctrl = (dma_hw->ch[dma_ctrl_channel].al1_ctrl & ~DMA_CH0_CTRL_TRIG_CHAIN_TO_BITS) | (dma_ctrl_channel << DMA_CH0_CTRL_TRIG_CHAIN_TO_LSB);
    dma_hw->ch[dma_channel].al1_ctrl = (dma_hw->ch[dma_channel].al1_ctrl & ~DMA_CH0_CTRL_TRIG_CHAIN_TO_BITS) | (dma_channel << DMA_CH0_CTRL_TRIG_CHAIN_TO_LSB);
    // Abort any in-progress DMA transfer
    dma_safe_abort(dma_ctrl_channel);
    //dma_channel_abort(dma_ctrl_channel);
    //dma_channel_abort(dma_channel);
    dma_safe_abort(dma_channel);
  }

  void Blinky::init() {

    if(blinky != nullptr) {
      // Tear down the old GU instance's hardware resources
      partial_teardown();
    }
                
    // for each row:
    //   for each bcd frame:
    //            0: 00001111                                     // row data & clock
    //            1: 00011111                                     // row pixel count (minus one)
    //      2  - 40: xxxxxxxv, xxxxxxxv, xxxxxxxv, ...            // pixel data)
    //      41 - 43: xxxxxxxx, xxxxxxxx, xxxxxxxx                 // dummy bytes to dword align
    //      44 - 47: tttttttt, tttttttt, tttttttt, tttttttt       // bcd tick count (0-65536)
    //
    //  .. and back to the start

    // initialise the bcd timing values and row selects in the bitstream
    for(uint8_t row = 0; row < ROW_COUNT; row++) {
      for(uint8_t frame = 0; frame < BCD_FRAME_COUNT; frame++) {
        // find the offset of this row and frame in the bitstream
        uint8_t *p = &bitstream[(row * ROW_BYTES) + (BCD_FRAME_BYTES * frame)];

        if(frame == 0) {
          if(row == 0)
            p[ 0] = 0b1101;  // row data high, toggle clock low, then high
          else
            p[ 0] = 0b1000;  // row data low, toggle clock low, then high
        }
        else {
          p[ 0] = 0b0000;    // row data low, clock low
        }
        p[ 1] = WIDTH - 1;                  // row pixel count

        // set the number of bcd ticks for this frame
        uint32_t bcd_ticks = (1 << frame);
        p[44] = (bcd_ticks &       0xff) >>  0;
        p[45] = (bcd_ticks &     0xff00) >>  8;
        p[46] = (bcd_ticks &   0xff0000) >> 16;
        p[47] = (bcd_ticks & 0xff000000) >> 24;
      }
    }

    gpio_init(COLUMN_CLOCK); gpio_set_dir(COLUMN_CLOCK, GPIO_OUT); gpio_put(COLUMN_CLOCK, false);
    gpio_init(COLUMN_DATA); gpio_set_dir(COLUMN_DATA, GPIO_OUT); gpio_put(COLUMN_DATA, false);
    gpio_init(COLUMN_LATCH); gpio_set_dir(COLUMN_LATCH, GPIO_OUT); gpio_put(COLUMN_LATCH, false);
    gpio_init(COLUMN_BLANK); gpio_set_dir(COLUMN_BLANK, GPIO_OUT); gpio_put(COLUMN_BLANK, true);

    // initialise the row select, and set them to a non-visible row to avoid flashes during setup
    gpio_init(ROW_DATA); gpio_set_dir(ROW_DATA, GPIO_OUT); gpio_put(ROW_DATA, false);
    gpio_init(ROW_DATA_CLOCK); gpio_set_dir(ROW_DATA_CLOCK, GPIO_OUT); gpio_put(ROW_DATA_CLOCK, true);
    //gpio_init(ROW_REG_CLOCK); gpio_set_dir(ROW_REG_CLOCK, GPIO_OUT); gpio_put(ROW_REG_CLOCK, true);

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
    bitstream_pio = pio0;
    if(blinky == nullptr) {
      bitstream_sm = pio_claim_unused_sm(bitstream_pio, true);
      bitstream_sm_offset = pio_add_program(bitstream_pio, &blinky_program);
    }

    pio_gpio_init(bitstream_pio, COLUMN_CLOCK);
    pio_gpio_init(bitstream_pio, COLUMN_DATA);
    pio_gpio_init(bitstream_pio, COLUMN_LATCH);
    pio_gpio_init(bitstream_pio, COLUMN_BLANK);

    pio_gpio_init(bitstream_pio, ROW_DATA);
    pio_gpio_init(bitstream_pio, ROW_DATA_CLOCK);

    // set the blank and row pins to be high, then set all led driving pins as outputs.
    // This order is important to avoid a momentary flash
    const uint pins_to_set = 1 << COLUMN_BLANK;
    pio_sm_set_pins_with_mask(bitstream_pio, bitstream_sm, pins_to_set, pins_to_set);
    pio_sm_set_consecutive_pindirs(bitstream_pio, bitstream_sm, COLUMN_CLOCK, 6, true);

    pio_sm_config c = blinky_program_get_default_config(bitstream_sm_offset);

    // osr shifts right, autopull on, autopull threshold 8
    sm_config_set_out_shift(&c, true, true, 32);

    // configure out, set, and sideset pins
    sm_config_set_out_pins(&c, ROW_DATA, 2);
    sm_config_set_set_pins(&c, COLUMN_DATA, 3);
    sm_config_set_sideset_pins(&c, COLUMN_CLOCK);

    // join fifos as only tx needed (gives 8 deep fifo instead of 4)
    sm_config_set_fifo_join(&c, PIO_FIFO_JOIN_TX);

      // setup dma transfer for pixel data to the pio
    if(blinky == nullptr) {
      dma_channel = dma_claim_unused_channel(true);
      dma_ctrl_channel = dma_claim_unused_channel(true);
    }
    dma_channel_config ctrl_config = dma_channel_get_default_config(dma_ctrl_channel);
    channel_config_set_transfer_data_size(&ctrl_config, DMA_SIZE_32);
    channel_config_set_read_increment(&ctrl_config, false);
    channel_config_set_write_increment(&ctrl_config, false);
    channel_config_set_chain_to(&ctrl_config, dma_channel);

    dma_channel_configure(
      dma_ctrl_channel,
      &ctrl_config,
      &dma_hw->ch[dma_channel].read_addr,
      &bitstream_addr,
      1,
      false
    );


    dma_channel_config config = dma_channel_get_default_config(dma_channel);
    channel_config_set_transfer_data_size(&config, DMA_SIZE_32);
    channel_config_set_bswap(&config, false); // byte swap to reverse little endian
    channel_config_set_dreq(&config, pio_get_dreq(bitstream_pio, bitstream_sm, true));
    channel_config_set_chain_to(&config, dma_ctrl_channel); 

    dma_channel_configure(
      dma_channel,
      &config,
      &bitstream_pio->txf[bitstream_sm],
      NULL,
      BITSTREAM_LENGTH / 4,
      false);

    pio_sm_init(bitstream_pio, bitstream_sm, bitstream_sm_offset, &c);

    pio_sm_set_enabled(bitstream_pio, bitstream_sm, true);

    // start the control channel
    dma_start_channel_mask(1u << dma_ctrl_channel);

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

  void Blinky::dma_safe_abort(uint channel) {
    // Tear down the DMA channel.
    // This is copied from: https://github.com/raspberrypi/pico-sdk/pull/744/commits/5e0e8004dd790f0155426e6689a66e08a83cd9fc
    uint32_t irq0_save = dma_hw->inte0 & (1u << channel);
    hw_clear_bits(&dma_hw->inte0, irq0_save);

    dma_hw->abort = 1u << channel;

    // To fence off on in-flight transfers, the BUSY bit should be polled
    // rather than the ABORT bit, because the ABORT bit can clear prematurely.
    while (dma_hw->ch[channel].ctrl_trig & DMA_CH0_CTRL_TRIG_BUSY_BITS) tight_loop_contents();

    // Clear the interrupt (if any) and restore the interrupt masks.
    dma_hw->ints0 = 1u << channel;
    hw_set_bits(&dma_hw->inte0, irq0_save);
  }

  void Blinky::set_pixel(int x, int y, uint8_t v) {
    if(x < 0 || x >= WIDTH || y < 0 || y >= HEIGHT) return;

    // make those coordinates sane
    x = (WIDTH - 1) - x;
    //y = (HEIGHT - 1) - y;

    //v = (v * this->brightness) >> 8;
    //uint32_t gamma_v = (uint32_t)GAMMA_14BIT[v];

    uint32_t gamma_v = (uint32_t)GAMMA_14BIT[v] * this->brightness;
    gamma_v >>= 8;

    // for each row:
    //   for each bcd frame:
    //            0: 00011111                           // row pixel count (minus one)
    //      1  - 32: xxxxxbgr, xxxxxbgr, xxxxxbgr, ...  // pixel data
    //      33 - 35: xxxxxxxx, xxxxxxxx, xxxxxxxx       // dummy bytes to dword align
    //           36: xxxxrrrr                           // row select bits
    //      37 - 39: tttttttt, tttttttt, tttttttt       // bcd tick count (0-65536)
    //
    //  .. and back to the start

    // set the appropriate bits in the separate bcd frames
    for(uint8_t frame = 0; frame < BCD_FRAME_COUNT; frame++) {
      uint8_t *p = &bitstream[(y * ROW_BYTES) + (BCD_FRAME_BYTES * frame) + 2 + x];

      *p = (uint8_t)(gamma_v & 0b1);
      gamma_v >>= 1;
    }
  }

  void Blinky::set_brightness(float value) {
    value = value < 0.0f ? 0.0f : value;
    value = value > 1.0f ? 1.0f : value;
    // Max brightness is - in fact - 256 since it's applied with:
    // result = (channel * brightness) >> 8
    // eg: (255 * 256) >> 8 == 255
    this->brightness = floor(value * 256.0f);
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
