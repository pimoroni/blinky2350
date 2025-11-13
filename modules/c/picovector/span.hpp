#pragma once

#include <stdint.h>
#ifdef PICO
#include "hardware/interp.h"
#else
#define __not_in_flash_func(v) v
#endif
#include <cstring>

#define debug_printf(fmt, ...) fprintf(stdout, fmt, ##__VA_ARGS__)

inline uint32_t __not_in_flash_func(_make_col)(uint8_t r, uint8_t g, uint8_t b, uint8_t a = 255) {
  return __builtin_bswap32((r << 24) | (g << 16) | (b << 8) | a);
}

inline uint8_t __not_in_flash_func(_r)(uint32_t c) { return ((uint8_t*)&c)[0]; }
inline uint8_t __not_in_flash_func(_g)(uint32_t c) { return ((uint8_t*)&c)[1]; }
inline uint8_t __not_in_flash_func(_b)(uint32_t c) { return ((uint8_t*)&c)[2]; }
inline uint8_t __not_in_flash_func(_a)(uint32_t c) { return ((uint8_t*)&c)[3]; }


inline void __not_in_flash_func(_rgba_blend_to)(uint32_t *dst, uint32_t *src) {
  uint8_t *pd = (uint8_t *)dst;
  uint8_t *ps = (uint8_t *)src;
  uint8_t a = ps[3];
  if(a == 255) {
    *dst = *src;
    return;
  }
  if(a == 0) {
    return;
  }
  #ifdef PICO_INTERP
    interp0->accum[1] = a; // alpha

    interp0->base[0] = pd[0];
    interp0->base[1] = ps[0]; // red
    pd[0] = (uint8_t)interp0->peek[1];

    interp0->base[0] = pd[1];
    interp0->base[1] = ps[1]; // green
    pd[1] = (uint8_t)interp0->peek[1];

    interp0->base[0] = pd[2];
    interp0->base[1] = ps[2]; // blue
    pd[2] = (uint8_t)interp0->peek[1];

    pd[3] = 255; // TODO: this is wrong
  #else
    pd[0] = (uint8_t)((ps[0] * a + pd[0] * (255 - a)) >> 8);
    pd[1] = (uint8_t)((ps[1] * a + pd[1] * (255 - a)) >> 8);
    pd[2] = (uint8_t)((ps[2] * a + pd[2] * (255 - a)) >> 8);
    pd[3] = 255;
  #endif
}

inline void __not_in_flash_func(_rgba_blend_to)(uint32_t *dst, uint32_t *src, uint8_t a) {
  uint8_t *pd = (uint8_t *)dst;
  uint8_t *ps = (uint8_t *)src;

  uint16_t t = a * ps[3] + 128;       // add 128 for rounding
  a = (t + (t >> 8)) >> 8;

  //a = (a * ps[3]) / 255;
  if(a == 255) {
    *dst = *src;
    return;
  }
  if(a == 0) {
    return;
  }

  #ifdef PICO_INTERP
    interp0->accum[1] = a; // alpha

    interp0->base[0] = pd[0];
    interp0->base[1] = ps[0]; // red
    pd[0] = (uint8_t)interp0->peek[1];

    interp0->base[0] = pd[1];
    interp0->base[1] = ps[1]; // green
    pd[1] = (uint8_t)interp0->peek[1];

    interp0->base[0] = pd[2];
    interp0->base[1] = ps[2]; // blue
    pd[2] = (uint8_t)interp0->peek[1];

    pd[3] = 255; // TODO: this is wrong
  #else
    pd[0] = (uint8_t)((ps[0] * a + pd[0] * (255 - a)) >> 8);
    pd[1] = (uint8_t)((ps[1] * a + pd[1] * (255 - a)) >> 8);
    pd[2] = (uint8_t)((ps[2] * a + pd[2] * (255 - a)) >> 8);
    pd[3] = 255;
  #endif
}

inline void __not_in_flash_func(span_argb8)(uint32_t *dst, int32_t w, uint32_t c) {
  while(w--) {
    _rgba_blend_to(dst++, &c);
  }
}


inline void __not_in_flash_func(span_argb8)(uint32_t *dst, int32_t w, uint32_t c, uint8_t *m) {
  while(w--) {
    _rgba_blend_to(dst++, &c, *m++);
  }
}

inline void __not_in_flash_func(span_blit_argb8)(uint32_t *src, uint32_t *dst, int w, int a = 255) {
  while(w--) {
    uint8_t *ps = (uint8_t *)src;
    uint8_t *pd = (uint8_t *)dst;

    int ca = (ps[3] * (a)) / 255; // apply global alpha

    if(ca == 0) {
      // zero alpha, skip pixel
    } else if (ca == 255) {
      // full alpha copy pixel
      *dst = *src;
    } else {
#ifdef PICO_INTERP
      // alpha requires blending pixel
      interp0->accum[1] = ca;

      interp0->base[0] = pd[0];
      interp0->base[1] = ps[0]; // red
      pd[1] = (uint8_t)interp0->peek[0];

      interp0->base[0] = pd[1];
      interp0->base[1] = ps[1]; // green
      pd[1] = (uint8_t)interp0->peek[1];

      interp0->base[0] = pd[2];
      interp0->base[1] = ps[2]; // blue
      pd[2] = (uint8_t)interp0->peek[1];
#else
      pd[0] = (uint8_t)((ps[0] * ca + pd[0] * (255 - ca)) >> 8);
      pd[1] = (uint8_t)((ps[1] * ca + pd[1] * (255 - ca)) >> 8);
      pd[2] = (uint8_t)((ps[2] * ca + pd[2] * (255 - ca)) >> 8);
      pd[3] = 255;
#endif
    }

    src++;
    dst++;
  }
}

inline void __not_in_flash_func(span_blit_argb8_palette)(void *vsrc, void *vdst, uint32_t *palette, int w, int a = 255) {
  uint8_t *src = (uint8_t*)vsrc;
  uint32_t *dst = (uint32_t*)vdst;

  while(w--) {
    uint32_t sc = palette[*src];
    uint8_t *ps = (uint8_t *)&sc;
    uint8_t *pd = (uint8_t *)dst;

    int ca = (ps[3] * (a)) / 255; // apply global alpha

    if(ca == 0) {
    } else if (ca == 255) {
      // full alpha copy pixel
      *dst = sc;
      //pd[3] = 255;
    } else {
#ifdef PICO_INTERP
      // alpha requires blending pixel
      interp0->accum[1] = ca;

      interp0->base[0] = pd[0];
      interp0->base[1] = ps[0]; // red
      pd[1] = (uint8_t)interp0->peek[0];

      interp0->base[0] = pd[1];
      interp0->base[1] = ps[1]; // green
      pd[1] = (uint8_t)interp0->peek[1];

      interp0->base[0] = pd[2];
      interp0->base[1] = ps[2]; // blue
      pd[2] = (uint8_t)interp0->peek[1];
#else
      pd[0] = ((pd[0] * (255 - ca)) + (ps[0] * ca)) / 255;
      pd[1] = ((pd[1] * (255 - ca)) + (ps[1] * ca)) / 255;
      pd[2] = ((pd[2] * (255 - ca)) + (ps[2] * ca)) / 255;
      pd[3] = 255;
#endif
    }
    src++;
    dst++;
  }
}


inline void __not_in_flash_func(span_blit_scale)(uint32_t *src, uint32_t *dst, int srcx, int srcstepx, int w, int a) {
  while(w--) {
    uint8_t *pd = (uint8_t *)dst;
    uint8_t *ps = (uint8_t *)(src + (srcx >> 16));

    int ca = (ps[3] * (a + 1)) / 256; // apply global alpha

    if(ca == 0) {
      // zero alpha, skip pixel
    } else if (ca == 255) {
      // full alpha copy pixel
      *dst = src[srcx >> 16];
    } else {
#ifdef PICO_INTERP
      // alpha requires blending pixel
      interp0->accum[1] = ca;

      interp0->base[0] = pd[1];
      interp0->base[1] = ps[1]; // red
      pd[1] = (uint8_t)interp0->peek[1];

      interp0->base[0] = pd[2];
      interp0->base[1] = ps[2]; // green
      pd[2] = (uint8_t)interp0->peek[1];

      interp0->base[0] = pd[3];
      interp0->base[1] = ps[3]; // blue
      pd[3] = (uint8_t)interp0->peek[1];
#else
      pd[0] = ((pd[0] * (255 - ca)) + (ps[0] * ca)) / 255;
      pd[1] = ((pd[1] * (255 - ca)) + (ps[1] * ca)) / 255;
      pd[2] = ((pd[2] * (255 - ca)) + (ps[2] * ca)) / 255;
#endif
    }

    srcx += srcstepx;
    dst++;
  }
}


inline void __not_in_flash_func(span_blit_scale_palette)(void *vsrc, void *vdst, uint32_t *palette, int srcx, int srcstepx, int w, int a) {
  uint8_t *src = (uint8_t*)vsrc;
  uint32_t *dst = (uint32_t*)vdst;

  while(w--) {
    uint8_t *pd = (uint8_t *)dst;
    uint8_t *pps = (uint8_t *)(src + (srcx >> 16));

    uint32_t sc = palette[*pps];
    uint8_t *ps = (uint8_t *)&sc;

    int ca = (ps[3] * (a + 1)) / 256; // apply global alpha

    if(ca == 0) {
      // zero alpha, skip pixel
    } else if (ca == 255) {
      // full alpha copy pixel
      *dst = sc;
    } else {
#ifdef PICO_INTERP
      // alpha requires blending pixel
      interp0->accum[1] = ca;

      interp0->base[0] = pd[1];
      interp0->base[1] = ps[1]; // red
      pd[1] = (uint8_t)interp0->peek[1];

      interp0->base[0] = pd[2];
      interp0->base[1] = ps[2]; // green
      pd[2] = (uint8_t)interp0->peek[1];

      interp0->base[0] = pd[3];
      interp0->base[1] = ps[3]; // blue
      pd[3] = (uint8_t)interp0->peek[1];
#else
      pd[0] = ((pd[0] * (255 - ca)) + (ps[0] * ca)) / 255;
      pd[1] = ((pd[1] * (255 - ca)) + (ps[1] * ca)) / 255;
      pd[2] = ((pd[2] * (255 - ca)) + (ps[2] * ca)) / 255;
#endif
    }

    srcx += srcstepx;
    dst++;
  }
}
