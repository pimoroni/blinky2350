import powman
from badgeware import status


def safe_mode():
    print("Safe Mode: connect to the Badgeware IDE to repair your badge. Press RESET to restart.")
    status(("SAFE", "MODE"), color.rgb(60, 35, 0))


if powman.get_wake_reason() == powman.WAKE_DOUBLETAP:
    safe_mode()

else:
    try:
        with open("hardware_test.txt", "r"):
            import hardware_test   # noqa F401
    except OSError:
        pass

    try:
        __import__("/system/main")
    except ImportError:
        fatal_error("System Error!", "Could not find /system/main.py. Connect to the Badgeware IDE to reinstall it!")
