import powman
import cppmem
# Switch C++ memory allocations to use MicroPython's heap
cppmem.set_mode(cppmem.MICROPYTHON)

try:
    with open("hardware_test.txt", "r"):
        import hardware_test   # noqa F401
except OSError:
    pass


def copy_files():
    # Copy default files from readonly /system to editable /
    default_files = ["main.py", "secrets.py"]
    buf = bytearray(256)

    for filename in default_files:
        try:
            open(f"/{filename}", "r").read()
            open("/system/nocopy", "r").read()
        except OSError:
            with open(f"/system/{filename}", "r") as system_main:
                with open(f"/{filename}", "w") as main:
                    while True:
                        length = system_main.readinto(buf)
                        if not length:
                            break
                        main.write(buf[:length])


if powman.get_wake_reason() == powman.WAKE_WATCHDOG:
    copy_files()


import picovector
import builtins

# Import PicoSystem module constants to builtins,
# so they are available globally.
for k, v in picovector.__dict__.items():
    if not k.startswith("__"):
        setattr(builtins, k, v)

setattr(builtins, "screen", picovector.screen)
