import time

import ide
import powman
from badgeware import scroller


def safe_mode():
    message = "Safe Mode: connect to the Badgeware IDE to repair your badge. Press RESET to restart."
    print(message)
    draw = scroller(message, color.rgb(60, 35, 0))
    while True:
        draw()
        time.sleep_ms(20)


ide.serve()

if powman.get_wake_reason() == powman.WAKE_DOUBLETAP:
    safe_mode()

else:
    try:
        with open("hardware_test.txt", "r"):
            import hardware_test   # noqa F401
    except OSError:
        pass

    if not file_exists("/apps/menu/__init__.py"):
        fatal_error("System Error!", "Could not find the launcher in /apps/menu. Connect to the Badgeware IDE to reinstall it!")

    badge.poll()
    app_to_launch = launch("/apps/menu")

    if app_to_launch is not None:
        while badge.pressed() or badge.held() or badge.released():
            badge.poll()
        launch(app_to_launch)

    reset()
