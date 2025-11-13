#include "blinky.h"


/***** Methods *****/
MP_DEFINE_CONST_FUN_OBJ_1(Blinky___del___obj, Blinky___del__);
MP_DEFINE_CONST_FUN_OBJ_1(Blinky_clear_obj, Blinky_clear);
MP_DEFINE_CONST_FUN_OBJ_1(Blinky_update_obj, Blinky_update);
MP_DEFINE_CONST_FUN_OBJ_2(Blinky_set_brightness_obj, Blinky_set_brightness);
MP_DEFINE_CONST_FUN_OBJ_1(Blinky_get_brightness_obj, Blinky_get_brightness);
MP_DEFINE_CONST_FUN_OBJ_2(Blinky_adjust_brightness_obj, Blinky_adjust_brightness);

/***** Binding of Methods *****/
static const mp_rom_map_elem_t Blinky_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR___del__), MP_ROM_PTR(&Blinky___del___obj) },
    { MP_ROM_QSTR(MP_QSTR_clear), MP_ROM_PTR(&Blinky_clear_obj) },
    { MP_ROM_QSTR(MP_QSTR_update), MP_ROM_PTR(&Blinky_update_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_brightness), MP_ROM_PTR(&Blinky_set_brightness_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_brightness), MP_ROM_PTR(&Blinky_get_brightness_obj) },
    { MP_ROM_QSTR(MP_QSTR_adjust_brightness), MP_ROM_PTR(&Blinky_adjust_brightness_obj) },

    { MP_ROM_QSTR(MP_QSTR_WIDTH), MP_ROM_INT(39) },
    { MP_ROM_QSTR(MP_QSTR_HEIGHT), MP_ROM_INT(26) }
};

static MP_DEFINE_CONST_DICT(Blinky_locals_dict, Blinky_locals_dict_table);

/***** Class Definition *****/
MP_DEFINE_CONST_OBJ_TYPE(
    Blinky_type,
    MP_QSTR_Blinky,
    MP_TYPE_FLAG_NONE,
    make_new, Blinky_make_new,
    buffer, Blinky_get_framebuffer,
    print, Blinky_print,
    locals_dict, (mp_obj_dict_t*)&Blinky_locals_dict
);

/***** Globals Table *****/
static const mp_map_elem_t blinky_globals_table[] = {
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_blinky) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_Blinky), (mp_obj_t)&Blinky_type },
};
static MP_DEFINE_CONST_DICT(mp_module_blinky_globals, blinky_globals_table);

/***** Module Definition *****/
const mp_obj_module_t blinky_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_blinky_globals,
};

MP_REGISTER_MODULE(MP_QSTR_blinky, blinky_user_cmodule);
