import curses

from utils import end_curses, init_curses


class MultiSelect:
    def __init__(self, options, header=None, selected_by_default=False):
        self.__options = [
            {
                "label": option["label"],
                "value": option["value"],
                "selected": selected_by_default,
            }
            for option in options
        ]
        self.__header = header
        self.__current_option = 0

    def get(self) -> list:
        self.__current_option = 0
        selected = []
        try:
            stdscr = init_curses()
            selected = self.__get(stdscr)
        except KeyboardInterrupt as e:
            raise e
        finally:
            end_curses(stdscr)

        return selected

    def __get(self, stdscr: curses.window) -> list:
        while True:
            stdscr.clear()

            if self.__header:
                stdscr.addstr(f"{self.__header}\n")
            else:
                stdscr.addstr("Wybierz opcje\n")

            stdscr.addstr("===========================================\n")

            for i, option in enumerate(self.__options):
                label = (
                    f"[x] {option['label']}"
                    if option["selected"]
                    else f"[ ] {option['label']}"
                )

                if i == self.__current_option:
                    stdscr.addstr(f"> {label}\n", curses.color_pair(1))
                else:
                    stdscr.addstr(f"  {label}\n")

            stdscr.addstr("===========================================\n")
            stdscr.addstr("↑ ↓ - poruszanie się\n")
            stdscr.addstr("Spacja - zaznacz/odznacz\n")
            stdscr.addstr("Enter - zatwierdź\n")

            key = stdscr.getch()

            if key == curses.KEY_UP:
                self.__current_option = (self.__current_option - 1) % len(
                    self.__options
                )
            elif key == curses.KEY_DOWN:
                self.__current_option = (self.__current_option + 1) % len(
                    self.__options
                )
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return [
                    option["value"] for option in self.__options if option["selected"]
                ]
            elif key == ord(" "):
                self.__options[self.__current_option]["selected"] = not self.__options[
                    self.__current_option
                ]["selected"]
