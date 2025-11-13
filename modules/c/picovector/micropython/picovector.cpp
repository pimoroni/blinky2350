#include "mp_tracked_allocator.hpp"
// #include "../picovector.hpp"
// #include "../primitive.hpp"
// #include "../image.hpp"


extern int PicoVector_working_buffer[];

#include "brush.hpp"
#include "shape.hpp"
#include "font.hpp"
#include "pixel_font.hpp"
#include "image.hpp"
#include "input.hpp"
#include "matrix.hpp"

#include "mp_helpers.hpp"

using namespace picovector;

extern "C" {

  #include "py/runtime.h"

  int screen_width = 39;
  int screen_height = 26;
  uint32_t framebuffer[39 * 26];

  mp_obj_t modpicovector___init__(void) {
  
  #ifdef PICO
    // we need a way to set this up, but if the user wants to use the
    // interpolators in their own code they might modify the configuration..
    // do we have to do this everytime we're about to render something to be
    // sure or do we just say that this interpolator is out of bounds if you're
    // using pico graphics 2?
    interp_config cfg = interp_default_config();
    interp_config_set_blend(&cfg, true);
    interp_set_config(interp0, 0, &cfg);
    cfg = interp_default_config();
    interp_set_config(interp0, 1, &cfg);
  #endif

    return mp_const_none;
  }
  
  void modpicovector_attr(mp_obj_t self_in, qstr attr, mp_obj_t *dest) {
    if (dest[0] == MP_OBJ_NULL) {
      if (attr == MP_QSTR_screen) {
        image_obj_t *image = mp_obj_malloc_with_finaliser(image_obj_t, &type_Image);
        image->image = new(m_malloc(sizeof(image_t))) image_t(framebuffer, screen_width, screen_height);
        dest[0] = MP_OBJ_FROM_PTR(image);
      }
    }
  }

}
