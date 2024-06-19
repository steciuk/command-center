from get_key_press import SpecialKeys, get_key_press
from utils import clear_screen, print_special


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
            selected = self.__get()
        except KeyboardInterrupt as e:
            raise e

        return selected

    def __get(self):
        while True:
            clear_screen()

            if self.__header:
                print(f"{self.__header}")
            else:
                print("Uporządkuj elementy")

            print("===========================================")

            for i, option in enumerate(self.__options):
                label = f"{option['label']}"

                if i == self.__current_option:
                    if self.__is_option_selected:
                        print_special(f"  > {label}")
                    else:
                        print_special(f"> {label}")

                else:
                    print(f"  {label}")

            print("===========================================")
            print("↑ ↓ - poruszanie się")
            print("Spacja - wybierz/upuść element do przesunięcia")
            print("Enter - zatwierdź")

            key = get_key_press()

            if key == SpecialKeys.UP:
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
            elif key == SpecialKeys.DOWN:
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
            elif key == SpecialKeys.ENTER:
                return [option["value"] for option in self.__options]
            elif key == SpecialKeys.SPACE:
                self.__is_option_selected = not self.__is_option_selected
