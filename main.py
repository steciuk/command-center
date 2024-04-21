#!/usr/bin/env python3
import os
import time
import pwd

import cv2
from napi import NapiPy
from pypdf import PdfMerger


def clear_screen():
    os.system("clear")


def path_dnd_input(*prompts, is_dir=False, allow_empty=False):
    path = input("\n".join(prompts))
    path = path.strip().strip("'")

    if allow_empty and path == "":
        return path

    if is_dir:
        if not os.path.exists(path):
            raise FileNotFoundError("Podany folder nie istnieje")
        if not os.path.isdir(path):
            raise NotADirectoryError("Podano plik zamiast folderu")
    else:
        if not os.path.exists(path):
            raise FileNotFoundError("Podany plik nie istnieje")
        if os.path.isdir(path):
            raise IsADirectoryError("Podano folder zamiast pliku")

    return path


def press_enter_to_continue(message):
    clear_screen()
    print(message)
    input("Naciśnij Enter aby kontynuować...")


class ShutdownManager:
    __SHUTDOWN_SCHEDULE_PATH = "/run/systemd/shutdown/scheduled"

    def __init__(self):
        self.scheduled = self.__shutdown_scheduled_in_hours()

    def __shutdown_scheduled_in_hours(self):
        if os.path.exists(self.__SHUTDOWN_SCHEDULE_PATH):
            with open(self.__SHUTDOWN_SCHEDULE_PATH, "r", encoding="utf8") as f:
                line = f.readlines()[0]
                micro_secs = int(line.split("=")[1])
                hh_mm = time.strftime("%H:%M", time.localtime(micro_secs / 1000000))
                return hh_mm

        return None

    def schedule_shutdown(self):
        clear_screen()
        num_hours = input("Za ile godzin wyłączyć komputer? (0 - wróć): ")

        try:
            num_hours = int(num_hours)
        except ValueError:
            return

        if num_hours <= 0:
            return

        os.system(f"shutdown +{num_hours * 60}")
        self.scheduled = time.strftime(
            "%H:%M", time.localtime(time.time() + num_hours * 3600)
        )

    def cancel_shutdown(self):
        os.system("shutdown -c")
        self.scheduled = None


class PlexManager:
    def __init__(self):
        self.plex_present = self.__is_plex_present()
        self.plex_running = self.plex_present and self.__is_plex_running()

    def __is_plex_present(self):
        return (
            os.system("systemctl list-unit-files | grep plexmediaserver.service") == 0
        )

    def __is_plex_running(self):
        return os.system("systemctl is-active --quiet plexmediaserver") == 0

    def start_plex(self):
        clear_screen()
        os.system("sudo systemctl start plexmediaserver")
        self.plex_running = True

    def stop_plex(self):
        clear_screen()
        os.system("sudo systemctl stop plexmediaserver")
        self.plex_running = False


class SubtitlesDownloader:
    def __init__(self):
        self.napi = NapiPy()

    def menu(self):
        clear_screen()
        print("Witaj w pobieraczu napisów!")
        print("===========================================")

        options = []

        options.append({"label": "Wróć", "action": lambda: None})
        options.append(
            {
                "label": "Pobierz napisy automatycznie",
                "action": self.download_subtitles_auto,
            }
        )
        options.append(
            {
                "label": "Pobierz napisy ręcznie",
                "action": self.download_subtitles_manual,
            }
        )

        for i, option in enumerate(options):
            print(f"{i}. {option['label']}")

        last_selected = input("\nWybierz opcję i naciśnij Enter: ")

        try:
            last_selected = int(last_selected)
            if last_selected <= 0 or last_selected >= len(options):
                return
        except ValueError:
            return

        try:
            options[last_selected]["action"]()
        except Exception as e:
            press_enter_to_continue(f"{str(e)}\n\nWystąpił krytyczny błąd")

    def display_movie_fps_and_duration(self, path):
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        duration = frame_count / fps
        duration = time.strftime("%H:%M:%S", time.gmtime(duration))

        print(f"FPS: {fps:.3f}")
        print(f"Czas trwania: {duration}")

    def download_subtitles_auto(self):
        clear_screen()

        try:
            movie_path = path_dnd_input(
                "1. Przeciągnij i upuść tutaj plik filmu",
                "2. Naciśnij Enter",
                "",
                "Plik: ",
                is_dir=False,
            )
        except Exception as e:
            return press_enter_to_continue(str(e))

        subs_hash = self.napi.calc_hash(movie_path)

        _, _, subtitles = self.napi.download_subs(subs_hash)

        if subtitles:
            self.napi.move_subs_to_movie(subtitles, movie_path)
            return press_enter_to_continue("Poprawnie pobrano napisy!")

        clear_screen()
        print("Nie udało się dopasować napisów automatycznie, spróbuj ręcznie\n")
        self.download_subtitles_manual(movie_path)

    def download_subtitles_manual(self, movie_path=None):
        if movie_path is None:
            clear_screen()

            try:
                movie_path = path_dnd_input(
                    "1. Przeciągnij i upuść tutaj plik filmu",
                    "2. Naciśnij Enter",
                    "",
                    "Plik: ",
                    is_dir=False,
                )
            except Exception as e:
                return press_enter_to_continue(str(e))

            clear_screen()

        try:
            self.display_movie_fps_and_duration(movie_path)
        except Exception as _:
            return press_enter_to_continue(
                "Podany plik najprawdopodobniej nie jest filmem, jest uszkodzony, bądź ma nieobsługiwany format"
            )

        print(
            "\n".join(
                [
                    "",
                    "1. Wejdź na stronę https://www.napiprojekt.pl/napisy-szukaj",
                    "2. Wyszukaj film po tytule i wybierz pasujący wynik (https://imgur.com/a/yIAA3zG)",
                    "  - Upewnij się, że tytuł i rok filmu są zgodne z tymi z pliku",
                    "  - Jeśli nie ma wyników, spróbuj wyszukać po angielskim (lub polskim) tytule",
                    "  - Czasem po wybraniu wyniku napiprojekt otwiera nową stronę z reklamą,",
                    "    wtedy wróć do poprzedniej strony i ponów próbę wybrania wyniku",
                    "3. Kliknij przycisk 'napisy' (https://imgur.com/a/k2fVPjo)",
                    "4. Dopasuj napisy do czasu trwania i FPS filmu (https://imgur.com/a/GR0Hw1z)",
                    "  - Najłatwiej posortować wyniki po czasie trwania,",
                    "    klikając w nagłówek kolumny 'CZAS TRWANIA'",
                    "  - Jeśli jest kilka pasujących wyników, wybierz ten z największą ilością pobrań",
                    "5. Kliknij prawym przyciskiem myszy na nazwę pliku i wybierz 'Kopiuj odnośnik' (https://imgur.com/a/fPSGycC)",
                    "6. Wklej skopiowany hash poniżej (CTRL+SHIFT+V)",
                    "  - Hash powinien wyglądać tak: 'napiprojekt:1234567890abcdef1234567890abcdef'",
                    "7. Naciśnij Enter",
                    "",
                ]
            )
        )

        subs_hash = input("Hash: ")
        subs_hash = subs_hash.strip()
        if subs_hash.startswith("napiprojekt:"):
            subs_hash = subs_hash.split(":")[1]

        if len(subs_hash) != 32:
            return press_enter_to_continue("Podano niepoprawny hash")

        _, _, subtitles = self.napi.download_subs(subs_hash)

        if subtitles:
            self.napi.move_subs_to_movie(subtitles, movie_path)
            return press_enter_to_continue("Poprawnie pobrano napisy!")

        return press_enter_to_continue("Nie udało się pobrać napisów")


def print_welcome_message():
    usr = pwd.getpwuid(os.getuid())[0]

    match usr:
        case "tata":
            print("Cześć kochany Tatusiu! :*")
        case "ula":
            print("Cześć kochana Mamusiu! :*")
        case "pola":
            print("Cześć kochana Polciu! :*")
        case _:
            print(f"Witaj {usr}!")


def multiple_files_input(*prompts, allowed_extensions=None):
    allowed_extensions = [] if allowed_extensions is None else allowed_extensions
    file_path = None
    file_paths = set()
    file_paths_in_order = []

    while file_path != "":
        clear_screen()
        print("\n".join(prompts))

        if len(file_paths_in_order) > 0:
            print("\nDodane pliki:")
            for file in file_paths_in_order:
                print(f"- {file.split('/')[-1]}")

        try:
            file_path = path_dnd_input("", "Plik: ", allow_empty=True, is_dir=False)
        except Exception as e:
            press_enter_to_continue(str(e))
            continue

        if file_path == "":
            break

        if len(allowed_extensions) > 0:
            if not any(file_path.endswith(ext) for ext in allowed_extensions):
                press_enter_to_continue(
                    f"Podany plik nie jest obsługiwanym plikiem: {', '.join(allowed_extensions)}"
                )
                continue

        if file_path in file_paths:
            press_enter_to_continue("Podany plik został już dodany")
            continue

        file_paths.add(file_path)
        file_paths_in_order.append(file_path)

    return file_paths_in_order


def install_fonts():
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


def update_script():
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


class PdfManager:
    def menu(self):
        while True:
            clear_screen()
            print("Witaj w menedżerze PDFów!")
            print("===========================================")

            options = []

            options.append({"label": "Wróć", "action": lambda: None})
            options.append({"label": "Połącz dokumenty PDF", "action": self.merge_pdfs})
            options.append(
                {"label": "Konwertuj dokumenty do PDF", "action": self.convert_to_pdf}
            )
            options.append(
                {
                    "label": "Konwertuj dokumenty do PDF i połącz",
                    "action": self.convert_and_merge,
                }
            )

            for i, option in enumerate(options):
                print(f"{i}. {option['label']}")

            last_selected = input("\nWybierz opcję i naciśnij Enter: ")

            try:
                last_selected = int(last_selected)
                if last_selected == 0:
                    return
                if last_selected < 0 or last_selected >= len(options):
                    continue
            except ValueError:
                continue

            try:
                options[last_selected]["action"]()
            except Exception as e:
                press_enter_to_continue(f"{str(e)}\n\nWystąpił krytyczny błąd")

    def merge_pdfs(self, document_paths=None):
        if document_paths is None:
            document_paths = multiple_files_input(
                "1. Pojedynczo przeciągaj i upuszczaj pliki do połączenia tutaj",
                "  - Wspierane formaty: .pdf",
                "2. Naciśnij Enter po każdym upuszczonym pliku",
                "3. Po zakończeniu naciśnij Enter jeszcze raz",
                allowed_extensions=[".pdf"],
            )

            if len(document_paths) == 0:
                return press_enter_to_continue("Nie wybrano żadnych dokumentów")

        clear_screen()
        try:
            output_path = path_dnd_input(
                "1. Przeciągnij i upuść folder, do którego ma być zapisany plik PDF",
                "2. Naciśnij Enter",
                "",
                "Folder: ",
                is_dir=True,
            )
        except Exception as e:
            return press_enter_to_continue(str(e))

        clear_screen()
        file_name = input("Podaj nazwę pliku wyjściowego: ")
        file_name = file_name.strip()
        if file_name == "":
            return press_enter_to_continue("Nie podano nazwy pliku wyjściowego")

        if not file_name.endswith(".pdf"):
            file_name += ".pdf"

        merger = PdfMerger()
        for document_path in document_paths:
            merger.append(document_path)

        merger.write(os.path.join(output_path, file_name))
        merger.close()

        press_enter_to_continue("Poprawnie połączono dokumenty w jeden plik PDF!")

    def convert_to_pdf(self, save=True):
        document_paths = multiple_files_input(
            "1. Pojedynczo przeciągaj i upuszczaj pliki do konwersji tutaj",
            "  - Wspierane formaty: .doc, .docx, .odt, .odf",
            "2. Naciśnij Enter po każdym upuszczonym pliku",
            "3. Po zakończeniu naciśnij Enter jeszcze raz",
            allowed_extensions=[".doc", ".docx", ".odt", ".odf"],
        )

        if len(document_paths) == 0:
            return press_enter_to_continue("Nie wybrano żadnych dokumentów")

        if save:
            clear_screen()
            try:
                output_dir = path_dnd_input(
                    "1. Przeciągnij i upuść folder, do którego mają być zapisane pliki PDF",
                    "2. Naciśnij Enter",
                    "",
                    "Folder: ",
                    is_dir=True,
                )
            except Exception as e:
                return press_enter_to_continue(str(e))
        else:
            output_dir = "/tmp/command_center"

        clear_screen()
        try:
            escaped_document_paths = [f"'{doc}'" for doc in document_paths]
            command = f"lowriter --convert-to pdf {' '.join(escaped_document_paths)} --outdir '{output_dir}'"
            os.system(command)
        except Exception as e:
            return press_enter_to_continue(str(e))

        if save:
            press_enter_to_continue("Poprawnie skonwertowano dokumenty do PDF!")

        output_files = [
            os.path.join(
                output_dir, ".".join(doc.split("/")[-1].split(".")[:-1]) + ".pdf"
            )
            for doc in document_paths
        ]
        return output_files

    def convert_and_merge(self):
        converted_files = self.convert_to_pdf(save=False)

        if converted_files is None or len(converted_files) == 0:
            return press_enter_to_continue(
                "Nie udało się skonwertować dokumentów do PDF"
            )

        self.merge_pdfs(converted_files)


def main():
    shutdown_manager = ShutdownManager()
    plex_manager = PlexManager()
    subtitles_downloader = SubtitlesDownloader()
    pdfs_manager = PdfManager()

    while True:
        clear_screen()
        print_welcome_message()

        print("===========================================")
        if shutdown_manager.scheduled:
            print(f"Wyłączenie komputera zaplanowane na {shutdown_manager.scheduled}")
        if plex_manager.plex_present:
            print(f"Plex: {'ON' if plex_manager.plex_running else 'OFF'}")
        print("===========================================")

        options = []

        options.append({"label": "Wyjdź", "action": exit})

        if shutdown_manager.scheduled:
            options.append(
                {
                    "label": "Anuluj wyłączenie komputera",
                    "action": shutdown_manager.cancel_shutdown,
                }
            )
        else:
            options.append(
                {
                    "label": "Zaplanuj wyłączenie komputera",
                    "action": shutdown_manager.schedule_shutdown,
                }
            )

        if plex_manager.plex_present:
            if plex_manager.plex_running:
                options.append(
                    {"label": "Wyłącz Plex", "action": plex_manager.stop_plex}
                )
            else:
                options.append(
                    {"label": "Włącz Plex", "action": plex_manager.start_plex}
                )

        options.append({"label": "Pobierz napisy", "action": subtitles_downloader.menu})
        options.append({"label": "Zainstaluj czcionki", "action": install_fonts})
        options.append({"label": "Zaktualizuj skrypt", "action": update_script})
        options.append({"label": "Zarządzaj PDFami", "action": pdfs_manager.menu})

        for i, option in enumerate(options):
            print(f"{i}. {option['label']}")

        last_selected = input("\nWybierz opcję i naciśnij Enter: ")

        try:
            last_selected = int(last_selected)
            if last_selected < 0 or last_selected >= len(options):
                continue
        except ValueError:
            continue

        try:
            options[last_selected]["action"]()
        except Exception as e:
            press_enter_to_continue(f"{str(e)}\n\nWystąpił krytyczny błąd")


if __name__ == "__main__":
    main()
