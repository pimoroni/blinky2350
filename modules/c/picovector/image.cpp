#include <string.h>
#include <math.h>
#include <algorithm>
#include <vector>

#include "image.hpp"
#include "span.hpp"
#include "brush.hpp"
#include "shape.hpp"

using std::vector;

namespace picovector {

  color_brush _default_image_brush(255, 255, 255, 255);

  image_t::image_t() {
  }

  image_t::image_t(image_t *source, rect_t r) {
    rect_t i = source->_bounds.intersection(r);
    *this = *source;
    this->_bounds = rect_t(0, 0, i.w, i.h);
    this->_buffer = source->ptr(i.x, i.y);
    this->_managed_buffer = false;
  }

  image_t::image_t(int w, int h, pixel_format_t pixel_format, bool has_palette) {
    _bounds = rect_t(0, 0, w, h);
    _brush = &_default_image_brush;
    _pixel_format = pixel_format;
    _has_palette = has_palette;
    _managed_buffer = true;
    _bytes_per_pixel = this->_has_palette ? sizeof(uint8_t) : sizeof(uint32_t);
    _row_stride = w * _bytes_per_pixel;
    _buffer = PV_MALLOC(this->buffer_size());
    if(_has_palette) {
      _palette.resize(256);
    }
  }

  image_t::image_t(void *buffer, int w, int h, pixel_format_t pixel_format, bool has_palette) {
    _bounds = rect_t(0, 0, w, h);
    _brush = &_default_image_brush;
    _pixel_format = pixel_format;
    _has_palette = has_palette;
    _buffer = buffer;
    _managed_buffer = false;
    debug_printf("has p %d\n", this->_has_palette);
    _bytes_per_pixel = this->_has_palette ? sizeof(uint8_t) : sizeof(uint32_t);
    _row_stride = w * _bytes_per_pixel;
    if(_has_palette) {
      _palette.resize(256);
    }
  }

  image_t::~image_t() {
    if(this->_managed_buffer) {
#ifdef PICO
      PV_FREE(this->_buffer);
#else
      PV_FREE(this->_buffer, this->buffer_size());
#endif
    }
  }

  size_t image_t::buffer_size() {
    return this->_bytes_per_pixel * this->_bounds.w * this->_bounds.h;
  }

  size_t image_t::bytes_per_pixel() {
    return this->_bytes_per_pixel;
  }

  bool image_t::compatible_buffer(image_t *other) {
    return this->_palette == other->_palette && this->_pixel_format == other->_pixel_format;
  }

  uint32_t image_t::row_stride() {
    return this->_row_stride;
  }

  rect_t image_t::bounds() {
    return this->_bounds;
  }

  bool image_t::has_palette() {
    return this->_has_palette;
  }

  void image_t::palette(uint8_t i, uint32_t c) {
    this->_palette[i] = c;
  }

  uint32_t image_t::palette(uint8_t i) {
    return this->_palette[i];
  }

  uint8_t image_t::alpha() {
    return this->_alpha;
  }

  void image_t::alpha(uint8_t alpha) {
    // TODO: check if pixel format and palette mode supports alpha
    this->_alpha = alpha;
  }

  antialias_t image_t::antialias() {
    return this->_antialias;
  }

  void image_t::antialias(antialias_t antialias) {
    // TODO: check if pixel format and palette mode supports alpha
    this->_antialias = antialias;
  }

  pixel_format_t image_t::pixel_format() {
    return this->_pixel_format;
  }

  void image_t::pixel_format(pixel_format_t pixel_format) {
    this->_pixel_format = pixel_format;
  }

  brush_t* image_t::brush() {
    return this->_brush;
  }

  void image_t::brush(brush_t *brush) {
    this->_brush = brush;
  }

  font_t* image_t::font() {
    return this->_font;
  }

  void image_t::font(font_t *font) {
    this->_font = font;
  }

  pixel_font_t* image_t::pixel_font() {
    return this->_pixel_font;
  }

  void image_t::pixel_font(pixel_font_t *pixel_font) {
    this->_pixel_font = pixel_font;
  }

  image_t image_t::window(rect_t r) {
    rect_t i = _bounds.intersection(r);
    image_t window = image_t(this, rect_t(i.x, i.y, i.w, i.h));
    return window;
  }

  void image_t::clear() {
    rectangle(_bounds);
  }

  void image_t::blit(image_t *t, const point_t p) {
    rect_t tr(p.x, p.y, _bounds.w, _bounds.h); // target rect
    tr = tr.intersection(t->_bounds); // clip to target image bounds

    if(tr.empty()) {return;}

    int sxo = p.x < 0 ? -p.x : 0;
    int syo = p.y < 0 ? -p.y : 0;

    for(int i = 0; i < tr.h; i++) {

      uint32_t *dst = (uint32_t *)t->ptr(tr.x, tr.y + i);

      if(this->_has_palette) {
        uint8_t *src = (uint8_t *)this->ptr(sxo, syo + i);
        span_blit_argb8_palette(src, dst, &this->_palette[0], tr.w, this->alpha());
      }else{
        uint32_t *src = (uint32_t *)this->ptr(sxo, syo + i);
        span_blit_argb8(src, dst, tr.w, this->alpha());
      }
    }
  }

  void image_t::blit(image_t *target, rect_t tr) {
    bool invert_x = tr.w < 0.0f;
    bool invert_y = tr.h < 0.0f;

    tr.w = abs(tr.w);
    tr.h = abs(tr.h);

    // clip the target rect to the target bounds
    rect_t ctr = tr.intersection(target->bounds());
    if(ctr.empty()) {return;}

    // calculate the source step
    float srcstepx = (invert_x ? -1 : 1) * this->_bounds.w / tr.w;
    float srcstepy = (invert_y ? -1 : 1) * this->_bounds.h / tr.h;

    // calculate the source offset
    float srcx = invert_x ? this->_bounds.w - 1 : 0;
    float srcy = invert_y ? this->_bounds.h - 1 : 0;
    srcx += (ctr.x - tr.x) * srcstepx;
    srcy += (ctr.y - tr.y) * srcstepy;

    int sy = ctr.y;// min(ctr.y, ctr.y + ctr.h);
    int ey = ctr.y + ctr.h;//max(ctr.y, ctr.y + ctr.h);

    for(int y = sy; y < ey; y++) {
      void *dst = target->ptr(ctr.x, y);

      if(this->_has_palette) {
        span_blit_scale_palette((uint32_t *)this->ptr(0, int(srcy)), (uint32_t *)dst, &this->_palette[0], int(srcx * 65536.0f), int(srcstepx * 65536.0f), abs(ctr.w), this->alpha());
      }else{
        span_blit_scale((uint32_t *)this->ptr(0, int(srcy)), (uint32_t *)dst, int(srcx * 65536.0f), int(srcstepx * 65536.0f), abs(ctr.w), this->alpha());
      }

      srcy += srcstepy;
    }
  }

  void* image_t::ptr(int x, int y) {
    //debug_printf("get ptr at %d, %d (bpp = %d, rs = %d)\n", x, y, (int)this->_bytes_per_pixel, (int)this->_row_stride);
    return (uint8_t *)(this->_buffer) + (x * this->_bytes_per_pixel) + (y * this->_row_stride);
  }

  void image_t::draw(shape_t *shape) {
    render(shape, this, &shape->transform, _brush);
  }

  void image_t::rectangle(const rect_t &r) {
    for(int y = 0; y < r.h; y++) {
      this->_brush->render_span(this, r.x, y, r.w);
    }
  }


  void image_t::circle(const point_t &p, const int &r) {
    // int sy = max(p.y - r, 0);
    // int ey = min(p.y + r, bounds.h);
    // for(int y = sy; y < ey; y++) {
    //   int w = sqrt((r * r) - ((y - p.y) * (y - p.y)));
    //   int sx = p.x - w;
    //   int ex = p.x + w;
    //   if(ex < 0 || sx >= bounds.h) {continue;}
    //   sx = max(sx, 0);
    //   ex = min(ex, bounds.w);

    //   //printf("c: %d -> %d @ %d\n", sx, ex, y);
    //   span_argb8(ptr(sx, y), ex - sx, c);
    // }
  }


  uint32_t image_t::pixel_unsafe(int x, int y) {
    return *((uint32_t *)ptr(x, y));
  }

  uint32_t image_t::pixel(int x, int y) {
    x = max(int(_bounds.x), min(x, int(_bounds.x + _bounds.w - 1)));
    y = max(int(_bounds.y), min(y, int(_bounds.y + _bounds.h - 1)));
    return *((uint32_t *)ptr(x, y));
  }

}