import sys
import termios
import tty


class SpecialKeys:
    UP = "\x1b[A"
    DOWN = "\x1b[B"
    RIGHT = "\x1b[C"
    LEFT = "\x1b[D"
    ENTER = "\r"
    SPACE = " "


def get_key_press():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        if key == "\x1b":
            key += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if key == "\x03":
        raise KeyboardInterrupt

    return key
