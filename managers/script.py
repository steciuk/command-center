import os
from utils import clear_screen, path_dnd_input, press_enter_to_continue


class ScriptUpdater:
    def update_script(self):
        SCRIPT_PATH = os.path.dirname(__file__)
        PYTHON_PATH = os.path.join(SCRIPT_PATH, ".venv/bin/python3")

        clear_screen()
        try:
            requirements_path = path_dnd_input(
                "1. Żeby zaktualizować skrypt, potrzebny jest plik 'main.py' oraz opcjonalnie 'requirements.txt'",
                "2. Jeśli posiadasz plik 'requirements.txt', przeciągnij i upuść go tutaj i naciśnij Enter, w przeciwnym wypadku po prostu naciśnij Enter",
                "",
                "Plik: ",
                is_dir=False,
                allow_empty=True,
            )
        except Exception as e:
            return press_enter_to_continue(str(e))

        if requirements_path != "":
            if not requirements_path.endswith("requirements.txt"):
                return press_enter_to_continue(
                    "Podany plik nie jest plikiem 'requirements.txt'"
                )

            clear_screen()
            os.system(f"{PYTHON_PATH} -m pip install -r '{requirements_path}'")

        clear_screen()
        try:
            main_path = path_dnd_input(
                "1. Przeciągnij i upuść plik 'main.py' tutaj",
                "2. Naciśnij Enter",
                "",
                "Plik: ",
                is_dir=False,
            )
        except Exception as e:
            return press_enter_to_continue(str(e))

        if not main_path.endswith("main.py"):
            return press_enter_to_continue("Podany plik nie jest plikiem 'main.py'")

        os.system(f"cp '{main_path}' {SCRIPT_PATH}")

        press_enter_to_continue("Zaktualizowano skrypt!\nUruchom skrypt ponownie")
        exit()
