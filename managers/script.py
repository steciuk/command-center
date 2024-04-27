import os
from menu import Menu
from utils import ROOT_DIR, press_enter_to_continue


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

    def __run_git_command(self, command):
        return os.system(f"git --git-dir={os.path.join(ROOT_DIR, '.git')} {command}")

    def __check_updates_available(self):
        if self.__run_git_command("fetch") != 0:
            press_enter_to_continue(
                "Nie udało się sprawdzić dostępnych aktualizacji\nCzy sklonowałeś repozytorium?"
            )
            return

        diff_output = self.__run_git_command("diff HEAD origin/main").read()
        if diff_output:
            self.__are_updates = True
        else:
            press_enter_to_continue("Brak dostępnych aktualizacji")

    def __update_script(self):
        python_path = os.path.join(os.path.dirname(__file__), ".venv/bin/python3")

        if self.__run_git_command("reset --hard") != 0:
            press_enter_to_continue("Nie udało się zaktualizować skryptu")
            return

        os.system(f"{python_path} -m pip install -r requirements.txt")

        press_enter_to_continue("Zaktualizowano!\nUruchom skrypt ponownie")
        exit()
