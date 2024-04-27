import os

from menu import Menu
from multi_select import MultiSelect
from utils import clear_screen, multiple_files_input, press_enter_to_continue


class FontManager:
    def __init__(self) -> None:
        self.__otf_path = "/usr/share/fonts/opentype/installed"
        self.__ttf_path = "/usr/share/fonts/truetype/installed"

        self.menu = (
            Menu()
            .with_header("Witaj w menedżerze czcionek!")
            .with_return()
            .with_action("Zainstaluj czcionki", self.install_fonts)
            .with_action("Odinstaluj czcionki", self.uninstall_fonts)
        )

    def uninstall_fonts(self):
        clear_screen()
        ttfs = (
            [
                os.path.join(self.__ttf_path, file)
                for file in os.listdir(self.__ttf_path)
                if file.endswith(".ttf")
            ]
            if os.path.exists(self.__ttf_path)
            else []
        )
        ttfs = [file for file in ttfs if os.path.isfile(file)]
        ttfs = sorted(ttfs)
        otfs = (
            [
                os.path.join(self.__otf_path, file)
                for file in os.listdir(self.__otf_path)
                if file.endswith(".otf")
            ]
            if os.path.exists(self.__otf_path)
            else []
        )
        otfs = [file for file in otfs if os.path.isfile(file)]
        otfs = sorted(otfs)

        if len(ttfs) == 0 and len(otfs) == 0:
            return press_enter_to_continue("Brak zainstalowanych czcionek")

        files = ttfs + otfs

        multi_select = MultiSelect(
            [{"label": file.split("/")[-1], "value": file} for file in files],
            header="Wybierz czcionki do odinstalowania",
        )
        selected_files = multi_select.get()

        if len(selected_files) == 0:
            return press_enter_to_continue("Nie wybrano żadnych czcionek")

        clear_screen()
        for file in selected_files:
            os.system(f"sudo rm '{file}'")

        clear_screen()
        self.__refresh_fonts()
        press_enter_to_continue("Odinstalowano wybrane czcionki")

    def install_fonts(self):
        font_paths = multiple_files_input(
            "1. Pobierz interesujące Cię czcionki z internetu. Wymaganym formatem jest .ttf lub .otf",
            "  - https://fonts.google.com/",
            "  - https://www.dafont.com/",
            "  - https://www.fontsquirrel.com/",
            "  - https://www.fontspace.com/",
            "  - https://www.urbanfonts.com/",
            "  - https://www.1001freefonts.com/",
            "  - https://www.myfonts.com/",
            "2. Pojedynczo przeciągaj i upuszczaj pobrane pliki .otf i .ttf tutaj",
            "3. Naciśnij Enter po każdym upuszczonym pliku",
            "4. Po zakończeniu naciśnij Enter jeszcze raz",
            allowed_extensions=[".ttf", ".otf"],
        )

        if len(font_paths) == 0:
            return press_enter_to_continue("Nie wybrano żadnych czcionek")

        otfs = [font for font in font_paths if font.endswith(".otf")]
        ttfs = [font for font in font_paths if font.endswith(".ttf")]

        if len(otfs) > 0:
            clear_screen()
            os.system(f"sudo mkdir -p {self.__otf_path}")
            for otf in otfs:
                os.system(f"sudo cp -n '{otf}' {self.__otf_path}/")

        if len(ttfs) > 0:
            clear_screen()
            os.system(f"sudo mkdir -p {self.__ttf_path}")
            for ttf in ttfs:
                os.system(f"sudo cp -n '{ttf}' {self.__ttf_path}/")

        self.__refresh_fonts()

        press_enter_to_continue(
            "Zainstalowano wybrane czcionki! Możesz usunąć pobrane pliki czcionek"
        )

    def __refresh_fonts(self):
        clear_screen()
        os.system("sudo fc-cache -f -v")
