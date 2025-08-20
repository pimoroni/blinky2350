import os
import rp2
import vfs
import machine  # noqa: F401
import powman


# Try to mount the filesystem, and format the flash if it doesn't exist.
bdev = rp2.Flash()
try:
    fat = vfs.VfsFat(bdev)
    fat.label("Blinky2350")
    vfs.mount(fat, "/")
    os.listdir("/") # might fail with UnicodeError on corrupt FAT

except:  # noqa: E722
    vfs.VfsFat.mkfs(bdev)
    fat = vfs.VfsFat(bdev)
    fat.label("Blinky2350")
    vfs.mount(fat, "/")


if powman.get_wake_reason() == powman.WAKE_DOUBLETAP:
    rp2.enable_msc()

del os, vfs, bdev
