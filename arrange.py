import curses

from utils import end_curses, init_curses


class Arrange:
    def __init__(self, options, header=None):
        self.__options = [
            {
                "label": option["label"],
                "value": option["value"],
            }
            for option in options
        ]
        self.__header = header
        self.__current_option = 0
        self.__is_option_selected = False

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

    def __get(self, stdscr):
        while True:
            stdscr.clear()

            if self.__header:
                stdscr.addstr(f"{self.__header}\n")
            else:
                stdscr.addstr("Uporządkuj elementy\n")

            stdscr.addstr("===========================================\n")

            for i, option in enumerate(self.__options):
                label = f"{option['label']}"

                if i == self.__current_option:
                    if self.__is_option_selected:
                        stdscr.addstr(f"  > {label}\n", curses.color_pair(1))
                    else:
                        stdscr.addstr(f"> {label}\n", curses.color_pair(1))

                else:
                    stdscr.addstr(f"  {label}\n")

            stdscr.addstr("===========================================\n")
            stdscr.addstr("↑ ↓ - poruszanie się\n")
            stdscr.addstr("Spacja - wybierz/upuść element do przesunięcia\n")
            stdscr.addstr("Enter - zatwierdź\n")

            key = stdscr.getch()

            if key == curses.KEY_UP:
                if self.__is_option_selected:
                    if self.__current_option <= 0:
                        self.__current_option = 0
                        continue

                    self.__options.insert(
                        self.__current_option - 1,
                        self.__options.pop(self.__current_option),
                    )
                    self.__current_option = self.__current_option - 1
                else:
                    self.__current_option = (self.__current_option - 1) % len(
                        self.__options
                    )
            elif key == curses.KEY_DOWN:
                if self.__is_option_selected:
                    if self.__current_option >= len(self.__options) - 1:
                        self.__current_option = len(self.__options) - 1
                        continue

                    self.__options.insert(
                        self.__current_option + 1,
                        self.__options.pop(self.__current_option),
                    )
                    self.__current_option = self.__current_option + 1
                else:
                    self.__current_option = (self.__current_option + 1) % len(
                        self.__options
                    )
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return [option["value"] for option in self.__options]
            elif key == ord(" "):
                self.__is_option_selected = not self.__is_option_selected
