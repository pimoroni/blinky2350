import sys
import os

sys.path.insert(0, "/system/apps/startup")
os.chdir("/system/apps/startup")

from badgeware import run


def update():
    return False


if __name__ == "__main__":
    run(update)
