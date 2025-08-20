import os
import rp2
import vfs
import machine  # noqa: F401


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

del os, vfs, bdev
