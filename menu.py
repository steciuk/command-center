import curses
from typing import Callable, Optional

from utils import end_curses, init_curses, press_enter_to_continue


class Menu:
    def __init__(self):
        self.__options = []
        self.__current_option = 0
        self.__headers = []
        self.__footers = []
        self.__back = None
        self.__exit = None

        self.__options_to_show = []
        self.__headers_to_show = []
        self.__footers_to_show = []

    def with_header(
        self, header: str | Callable, condition: Optional[callable] = lambda: True
    ):
        self.__headers.append({"header": header, "condition": condition})
        return self

    def with_footer(
        self, footer: str | Callable, condition: Optional[callable] = lambda: True
    ):
        self.__footers.append({"footer": footer, "condition": condition})
        return self

    def with_submenu(
        self, label: str, menu: "Menu", condition: Optional[callable] = lambda: True
    ):
        self.__options.append(
            {
                "type": "menu",
                "label": label,
                "action": menu,
                "condition": condition,
            }
        )
        return self

    def with_action(
        self, label: str, action: callable, condition: Optional[callable] = lambda: True
    ):
        self.__options.append(
            {
                "type": "action",
                "label": label,
                "action": action,
                "condition": condition,
            }
        )
        return self

    def with_exit(self, condition: Optional[callable] = lambda: True):
        self.__exit = {
            "condition": condition,
        }
        return self

    def with_return(self, condition: Optional[callable] = lambda: True):
        self.__back = {
            "condition": condition,
        }
        return self

    def run(self):
        self.__current_option = 0

        try:
            try:
                stdscr = init_curses()
                stdscr = self.__run(stdscr)
            except Exception as e:
                raise e
            finally:
                end_curses(stdscr)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            press_enter_to_continue(f"{str(e)}\n\nWystąpił krytyczny błąd")

    def __refresh_options(self):
        self.__headers_to_show = [
            header["header"] for header in self.__headers if header["condition"]()
        ]
        self.__footers_to_show = [
            footer["footer"] for footer in self.__footers if footer["condition"]()
        ]
        self.__headers_to_show = [
            header() if callable(header) else header
            for header in self.__headers_to_show
        ]
        self.__footers_to_show = [
            footer() if callable(footer) else footer
            for footer in self.__footers_to_show
        ]

        self.__footers_to_show.append("↑ ↓ - poruszanie się")
        self.__footers_to_show.append("Enter - wybierz")

        self.__options_to_show = [
            {
                "type": option["type"],
                "label": option["label"],
                "action": option["action"],
            }
            for option in self.__options
            if option["condition"]()
        ]

        if self.__back is not None and self.__back["condition"]():
            self.__options_to_show.append(
                {"type": "return", "label": "Wróć", "action": None}
            )

        if self.__exit is not None and self.__exit["condition"]():
            self.__options_to_show.append(
                {"type": "exit", "label": "Wyjdź", "action": exit}
            )

        if len(self.__options_to_show) == 0:
            self.__options_to_show.append(
                {"type": "return", "label": "Wróć", "action": None}
            )

        if self.__current_option >= len(self.__options_to_show):
            self.__current_option = 0

    def __run(self, stdscr: curses.window) -> curses.window:
        self.__refresh_options()

        while True:
            stdscr.clear()

            if len(self.__headers_to_show) > 0:
                for header in self.__headers_to_show:
                    stdscr.addstr(f"{header}\n")
                stdscr.addstr("===========================================\n")

            for i, option in enumerate(self.__options_to_show):
                if i == self.__current_option:
                    stdscr.addstr(f"> {option['label']}\n", curses.color_pair(1))
                else:
                    stdscr.addstr(f"  {option['label']}\n")

            if len(self.__footers_to_show) > 0:
                stdscr.addstr("===========================================\n")
                for footer in self.__footers_to_show:
                    stdscr.addstr(f"{footer}\n")

            key = stdscr.getch()

            if key == curses.KEY_UP:
                self.__current_option = (self.__current_option - 1) % len(
                    self.__options_to_show
                )
            elif key == curses.KEY_DOWN:
                self.__current_option = (self.__current_option + 1) % len(
                    self.__options_to_show
                )
            elif key == curses.KEY_ENTER or key in [10, 13]:
                option = self.__options_to_show[self.__current_option]
                if option["type"] == "exit":
                    option["action"]()
                    break
                elif option["type"] == "return":
                    break
                elif option["type"] == "action":
                    end_curses(stdscr)
                    try:
                        option["action"]()
                    except KeyboardInterrupt as e:
                        raise e
                    except Exception as e:
                        press_enter_to_continue(f"{str(e)}\n\nWystąpił krytyczny błąd")

                    stdscr = init_curses()
                    self.__refresh_options()
                elif option["type"] == "menu":
                    end_curses(stdscr)
                    option["action"].run()
                    stdscr = init_curses()
                    self.__refresh_options()

        return stdscr
