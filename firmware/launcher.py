from picographics import PicoGraphics, DISPLAY_GENERIC, PEN_RGB888
display = PicoGraphics(display=DISPLAY_GENERIC,
                       width=39,
                       height=26,
                       pen_type=PEN_RGB888)
display.set_pen(0)
display.clear()
display.set_pen(0x22)
display.text("TODO", 1, 0, scale=1)
display.update()
