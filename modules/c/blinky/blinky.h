// Include MicroPython API.
#include "py/runtime.h"

/***** Extern of Class Definition *****/
extern const mp_obj_type_t Blinky_type;

/***** Extern of Class Methods *****/
extern void Blinky_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind);
extern mp_obj_t Blinky_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args);
extern mp_obj_t Blinky___del__(mp_obj_t self_in);
extern mp_obj_t Blinky_clear(mp_obj_t self_in);

extern mp_obj_t Blinky_update(mp_obj_t self_in);

extern mp_obj_t Blinky_set_brightness(mp_obj_t self_in, mp_obj_t value);
extern mp_obj_t Blinky_get_brightness(mp_obj_t self_in);
extern mp_obj_t Blinky_adjust_brightness(mp_obj_t self_in, mp_obj_t delta);

extern mp_int_t Blinky_get_framebuffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags);

