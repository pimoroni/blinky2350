#pragma once

#include "picovector.hpp"
#include "mat3.hpp"
#include "image.hpp"
#include "blend.hpp"

namespace picovector {

  // empty implementations for unsupported modes
  void pixel_func_nop(image_t *target, brush_t *brush, int x, int y);
  void span_func_nop(image_t *target, brush_t *brush, int x, int y, int w);
  void mask_span_func_nop(image_t *target, brush_t *brush, int x, int y, int w, uint8_t *m);

  struct brush_t {
    //pixel_func_t pixel_func;
    //span_func_t span_func;
    //mask_span_func_t mask_span_func;
    virtual pixel_func_t get_pixel_func(image_t *target) {return pixel_func_nop;};
    virtual span_func_t get_span_func(image_t *target) {return span_func_nop;};
    virtual mask_span_func_t get_mask_span_func(image_t *target) {return mask_span_func_nop;};
  };

  struct color_brush_t : public brush_t {
    uint32_t c;
    uint8_t r, g, b, a;

    color_brush_t(uint32_t c) : c(c) {
      r = get_r(&c);
      g = get_g(&c);
      b = get_b(&c);
      a = get_a(&c);
    };

    pixel_func_t get_pixel_func(image_t *target);
    span_func_t get_span_func(image_t *target);
    mask_span_func_t get_mask_span_func(image_t *target);
  };

  extern const uint8_t patterns[38][8];
  struct pattern_brush_t : public brush_t {
  public:
    uint8_t p[8];
    uint32_t c1;
    uint32_t c2;

    pattern_brush_t(uint32_t c1, uint32_t c2, uint8_t pattern_index);
    pattern_brush_t(uint32_t c1, uint32_t c2, uint8_t *pattern);

    pixel_func_t get_pixel_func(image_t *target);
    span_func_t get_span_func(image_t *target);
    mask_span_func_t get_mask_span_func(image_t *target);
  };

  struct image_brush_t : public brush_t {
  public:
    image_t *src;
    mat3_t inverse_transform;

    image_brush_t(image_t *src);
    image_brush_t(image_t *src, mat3_t *transform);

    pixel_func_t get_pixel_func(image_t *target);
    span_func_t get_span_func(image_t *target);
    mask_span_func_t get_mask_span_func(image_t *target);
  };

  // class brighten_brush : public brush_t {
  // public:
  //   int amount;
  //   brighten_brush(int amount) : amount(amount) {}
  //   void render_span(int x, int y, int w);
  //   void render_span_buffer(int x, int y, int w, uint8_t *sb) {};
  // };

  // class xor_brush : public brush_t {
  // public:
  //   uint32_t color;
  //   xor_brush(uint32_t color) : color(color) {}
  //   void render_span(int x, int y, int w);
  //   void render_span_buffer(int x, int y, int w, uint8_t *sb);
  // };

}