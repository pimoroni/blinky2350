import badgeware


def hold():
    message = "Connected: the Badgeware IDE is updating files. Press any button to cancel."
    print(message)
    return badgeware.scroller(message, color.rgb(0, 30, 60))


def safe_mode():
    message = "Safe Mode: connect to the Badgeware IDE to repair your badge. Press RESET to restart."
    print(message)
    return badgeware.scroller(message, color.rgb(60, 35, 0))


def error(_title, _message):
    badgeware.status(("ERR",), color.rgb(60, 0, 0))
