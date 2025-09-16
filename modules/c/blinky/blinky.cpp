#include "driver/blinky.hpp"
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
} ModPicoGraphics_obj_t;

/***** Print *****/
void Blinky_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void)kind; //Unused input parameter
    //_Blinky_obj_t *self = MP_OBJ_TO_PTR2(self_in, _Blinky_obj_t);
    mp_print_str(print, "Blinky()");
}


/***** Constructor *****/
mp_obj_t Blinky_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    (void)n_args;
    (void)n_kw;
    (void)all_args;

    _Blinky_obj_t *self = mp_obj_malloc_with_finaliser(_Blinky_obj_t, &Blinky_type);
    self->blinky = m_new_class(Blinky);
    self->blinky->init();

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
}