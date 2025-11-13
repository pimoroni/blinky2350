import powman
import cppmem
# Switch C++ memory allocations to use MicroPython's heap
cppmem.set_mode(cppmem.MICROPYTHON)

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


if powman.get_wake_reason() in (powman.WAKE_WATCHDOG, powman.WAKE_RESET):
    copy_files()
