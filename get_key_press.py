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


def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_key_press():
    key = get_char()

    if key == "\x1b":
        key += get_char()
        key += get_char()

    if key == "\x03":
        raise KeyboardInterrupt

    return key
