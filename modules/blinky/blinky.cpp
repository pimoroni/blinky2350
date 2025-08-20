#include "drivers/blinky/blinky.hpp"
#include "libraries/pico_graphics/pico_graphics.hpp"
#include "micropython/modules/util.hpp"
#include <cstdio>
#include <cfloat>


using namespace pimoroni;

extern "C" {
#include "blinky.h"
#include "micropython/modules/pimoroni_i2c/pimoroni_i2c.h"
#include "py/builtin.h"


/********** Blinky **********/

/***** Variables Struct *****/
typedef struct _Blinky_obj_t {
    mp_obj_base_t base;
    Blinky* blinky;
} _Blinky_obj_t;

typedef struct _ModPicoGraphics_obj_t {
    mp_obj_base_t base;
    PicoGraphics *graphics;
    DisplayDriver *display;
    void *spritedata;
    void *buffer;
    _PimoroniI2C_obj_t *i2c;
    //mp_obj_t scanline_callback; // Not really feasible in MicroPython
} ModPicoGraphics_obj_t;

/***** Print *****/
void Blinky_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void)kind; //Unused input parameter
    //_Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    mp_print_str(print, "Blinky()");
}


/***** Constructor *****/
mp_obj_t Blinky_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    _Blinky_obj_t *self = nullptr;

    enum { ARG_pio, ARG_sm, ARG_pins, ARG_common_pin, ARG_direction, ARG_counts_per_rev, ARG_count_microsteps, ARG_freq_divider };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_pio, MP_ARG_INT },
        { MP_QSTR_sm, MP_ARG_INT }
    };

    // Parse args.
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    int pio_int = args[ARG_pio].u_int;
    if(pio_int < 0 || pio_int > (int)NUM_PIOS) {
        mp_raise_ValueError(MP_ERROR_TEXT("pio out of range. Expected 0 to 2"));
    }
    //PIO pio = pio_int == 0 ? pio0 : pio1;

    int sm = args[ARG_sm].u_int;
    if(sm < 0 || sm > (int)NUM_PIO_STATE_MACHINES) {
        mp_raise_ValueError(MP_ERROR_TEXT("sm out of range. Expected 0 to 3"));
    }


    Blinky *blinky = m_new_class(Blinky);
    blinky->init();

    self = mp_obj_malloc_with_finaliser(_Blinky_obj_t, &Blinky_type);
    self->blinky = blinky;

    return MP_OBJ_FROM_PTR(self);
}


/***** Destructor ******/
mp_obj_t Blinky___del__(mp_obj_t self_in) {
    _Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    m_del_class(Blinky, self->blinky);
    return mp_const_none;
}


/***** Methods *****/
extern mp_obj_t Blinky_clear(mp_obj_t self_in) {
    _Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    self->blinky->clear();
    return mp_const_none;
}

extern mp_obj_t Blinky_update(mp_obj_t self_in, mp_obj_t graphics_in) {
    _Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    ModPicoGraphics_obj_t *picographics = MP_OBJ_TO_PTR2(graphics_in, ModPicoGraphics_obj_t);

    self->blinky->update(picographics->graphics);

    return mp_const_none;
}

extern mp_obj_t Blinky_set_brightness(mp_obj_t self_in, mp_obj_t value) {
    _Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    self->blinky->set_brightness(mp_obj_get_float(value));
    return mp_const_none;
}

extern mp_obj_t Blinky_get_brightness(mp_obj_t self_in) {
    _Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    return mp_obj_new_float(self->blinky->get_brightness());
}

extern mp_obj_t Blinky_adjust_brightness(mp_obj_t self_in, mp_obj_t delta) {
    _Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    self->blinky->adjust_brightness(mp_obj_get_float(delta));
    return mp_const_none;
}

extern mp_obj_t Blinky_is_pressed(mp_obj_t self_in, mp_obj_t button) {
    _Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    return mp_obj_new_bool(self->blinky->is_pressed((uint8_t)mp_obj_get_int(button)));
}
}