import os

from utils import clear_screen, multiple_files_input, press_enter_to_continue


class FontManager:
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
            os.system("sudo mkdir -p /usr/share/fonts/opentype/installed")
            for otf in otfs:
                os.system(f"sudo cp -n '{otf}' /usr/share/fonts/opentype/installed/")

        if len(ttfs) > 0:
            clear_screen()
            os.system("sudo mkdir -p /usr/share/fonts/truetype/installed")
            for ttf in ttfs:
                os.system(f"sudo cp -n '{ttf}' /usr/share/fonts/truetype/installed/")

        clear_screen()
        os.system("sudo fc-cache -f -v")

        press_enter_to_continue(
            "Zainstalowano wybrane czcionki! Możesz usunąć pobrane pliki czcionek"
        )
