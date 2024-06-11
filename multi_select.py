from get_key_press import SpecialKeys, get_key_press
from utils import clear_screen, press_enter_to_continue, print_special


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
            selected = self.__get()
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            press_enter_to_continue(f"{str(e)}\n\nWystąpił krytyczny błąd")

        return selected

    def __get(self) -> list:
        while True:
            clear_screen()

            if self.__header:
                print(f"{self.__header}")
            else:
                print("Wybierz opcje")

            print("===========================================")

            for i, option in enumerate(self.__options):
                label = (
                    f"[x] {option['label']}"
                    if option["selected"]
                    else f"[ ] {option['label']}"
                )

                if i == self.__current_option:
                    print_special(f"> {label}")
                else:
                    print(f"  {label}")

            print("===========================================")
            print("↑ ↓ - poruszanie się")
            print("Spacja - zaznacz/odznacz")
            print("Enter - zatwierdź")

            key = get_key_press()

            if key == SpecialKeys.UP:
                self.__current_option = (self.__current_option - 1) % len(
                    self.__options
                )
            elif key == SpecialKeys.DOWN:
                self.__current_option = (self.__current_option + 1) % len(
                    self.__options
                )
            elif key == SpecialKeys.ENTER:
                return [
                    option["value"] for option in self.__options if option["selected"]
                ]
            elif key == SpecialKeys.SPACE:
                self.__options[self.__current_option]["selected"] = not self.__options[
                    self.__current_option
                ]["selected"]
