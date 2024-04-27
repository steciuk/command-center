import os
from menu import Menu
from utils import press_enter_to_continue


class ScriptGitUpdater:
    def __init__(self) -> None:
        self.__are_updates = False

        if not self.__is_git_installed():
            self.menu = (
                Menu()
                .with_header("Do zaktualizowania skryptu wymagany jest Git")
                .with_return()
            )
        else:
            self.menu = (
                Menu()
                .with_header("Witaj w menedżerze aktualizacji skryptu!")
                .with_header(
                    "===========================================",
                    condition=lambda: self.__are_updates,
                )
                .with_header(
                    "Dostępna jest nowa wersja skryptu!",
                    condition=lambda: self.__are_updates,
                )
                .with_return()
                .with_action(
                    "Sprawdź dostępność aktualizacji", self.__check_updates_available
                )
                .with_action(
                    "Zaktualizuj skrypt",
                    self.__update_script,
                    condition=lambda: self.__are_updates,
                )
            )

    def __is_git_installed(self):
        return os.system("which git > /dev/null") == 0

    def __check_updates_available(self):
        os.system("git fetch")

        diff_output = os.popen("git diff HEAD origin/master").read()
        if diff_output:
            self.__are_updates = True
        else:
            press_enter_to_continue("Brak dostępnych aktualizacji")

    def __update_script(self):
        SCRIPT_PATH = os.path.dirname(__file__)
        PYTHON_PATH = os.path.join(SCRIPT_PATH, ".venv/bin/python3")

        os.system("git pull")
        os.system(f"{PYTHON_PATH} -m pip install -r requirements.txt")

        press_enter_to_continue("Zaktualizowano!\nUruchom skrypt ponownie")
        exit()
