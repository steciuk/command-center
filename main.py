#!/usr/bin/env python3
import os
import time
import pwd

import cv2
from napi import NapiPy
from pypdf import PdfMerger


def clear_screen():
    os.system("clear")


def path_dnd_input(*prompts, dir=False, allow_empty=False):
    path = input("\n".join(prompts))
    path = path.strip().strip("'")

    if allow_empty and path == "":
        return path

    if dir:
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


def schedule_shutdown():
    clear_screen()
    num_hours = input("Za ile godzin wyłączyć komputer? (0 - wróć): ")

    try:
        num_hours = int(num_hours)
    except ValueError:
        return

    if num_hours <= 0:
        return

    os.system(f"shutdown +{num_hours * 60}")


def cancel_shutdown():
    os.system("shutdown -c")


def is_plex_present():
    return os.system("systemctl list-unit-files | grep plexmediaserver.service") == 0


def is_plex_running():
    return os.system("systemctl is-active --quiet plexmediaserver") == 0


def start_plex():
    clear_screen()
    os.system("sudo systemctl start plexmediaserver")


def stop_plex():
    clear_screen()
    os.system("sudo systemctl stop plexmediaserver")


def shutdown_scheduled_in_hours():
    SHUTDOWN_SCHEDULE_PATH = "/run/systemd/shutdown/scheduled"

    if os.path.exists(SHUTDOWN_SCHEDULE_PATH):
        with open(SHUTDOWN_SCHEDULE_PATH, "r") as f:
            line = f.readlines()[0]
            mircosecs = int(line.split("=")[1])
            hh_mm = time.strftime("%H:%M", time.localtime(mircosecs / 1000000))
            return hh_mm

    return None


def seconds_to_hh_mm_ss(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def display_movie_fps_and_duration(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    duration = frame_count / fps

    duration = seconds_to_hh_mm_ss(duration)

    print(f"FPS: {fps:.3f}")
    print(f"Czas trwania: {duration}")


def download_subtitles_auto():
    clear_screen()

    try:
        movie_path = path_dnd_input(
            "1. Przeciągnij i upuść tutaj plik filmu",
            "2. Naciśnij Enter",
            "",
            "Plik: ",
            dir=False,
        )
    except Exception as e:
        return press_enter_to_continue(str(e))

    napi = NapiPy()
    hash = napi.calc_hash(movie_path)

    _, _, subtitles = napi.download_subs(hash)

    if subtitles:
        napi.move_subs_to_movie(subtitles, movie_path)
        return press_enter_to_continue("Poprawnie pobrano napisy!")

    clear_screen()
    print("Nie udało się dopasować napisów automatycznie, spróbuj ręcznie\n")
    download_subtitles_manual(movie_path)


def download_subtitles_manual(movie_path=None):
    if movie_path is None:
        clear_screen()

        try:
            movie_path = path_dnd_input(
                "1. Przeciągnij i upuść tutaj plik filmu",
                "2. Naciśnij Enter",
                "",
                "Plik: ",
                dir=False,
            )
        except Exception as e:
            return press_enter_to_continue(str(e))

        clear_screen()

    try:
        display_movie_fps_and_duration(movie_path)
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

    hash = input("Hash: ")
    hash = hash.strip()
    if hash.startswith("napiprojekt:"):
        hash = hash.split(":")[1]

    if len(hash) != 32:
        return press_enter_to_continue("Podano niepoprawny hash")

    napi = NapiPy()
    _, _, subtitles = napi.download_subs(hash)

    if subtitles:
        napi.move_subs_to_movie(subtitles, movie_path)
        return press_enter_to_continue("Poprawnie pobrano napisy!")

    press_enter_to_continue("Nie udało się pobrać napisów")


def subtitles_downloader():
    clear_screen()
    print("Witaj w pobieraczu napisów!")
    print("===========================================")

    options = []

    options.append({"label": "Wróć", "action": lambda: None})
    options.append(
        {"label": "Pobierz napisy automatycznie", "action": download_subtitles_auto}
    )
    options.append(
        {"label": "Pobierz napisy ręcznie", "action": download_subtitles_manual}
    )

    for i, option in enumerate(options):
        print(f"{i}. {option['label']}")

    last_selected = input("\nWybierz opcję i naciśnij Enter: ")

    try:
        last_selected = int(last_selected)
        if last_selected == 0:
            return
        if last_selected < 0 or last_selected >= len(options):
            return
    except ValueError:
        return

    try:
        options[last_selected]["action"]()
    except Exception as e:
        press_enter_to_continue(f"{str(e)}\n\nWystąpił krytyczny błąd")


def print_welcome_message():
    usr = pwd.getpwuid(os.getuid())[0]

    match usr:
        case "tata":
            print("Cześć kochany Tatusiu! :*")
        case "ula":
            print("Cześć kochana Mamusiu! :*")
        case _:
            print(f"Witaj {usr}!")


def multiple_files_input(prompt, allowed_extensions=[]):
    file_path = None
    file_paths = set()
    file_paths_in_order = []

    while file_path != "":
        clear_screen()
        print(prompt)

        if len(file_paths_in_order) > 0:
            print("\nDodane pliki:")
            for file in file_paths_in_order:
                print(f"- {file.split('/')[-1]}")

        try:
            file_path = path_dnd_input("", "Plik: ", allow_empty=True, dir=False)
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
        "\n".join(
            [
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
            ]
        ),
        [".ttf", ".otf"],
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
            dir=False,
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
            dir=False,
        )
    except Exception as e:
        return press_enter_to_continue(str(e))

    if not main_path.endswith("main.py"):
        return press_enter_to_continue("Podany plik nie jest plikiem 'main.py'")

    os.system(f"cp '{main_path}' {SCRIPT_PATH}")

    press_enter_to_continue("Zaktualizowano skrypt!\nUruchom skrypt ponownie")
    exit()


def merge_pdfs(document_paths=[]):
    if len(document_paths) == 0:
        document_paths = multiple_files_input(
            "\n".join(
                [
                    "1. Pojedynczo przeciągaj i upuszczaj pliki do połączenia tutaj",
                    "  - Wspierane formaty: .pdf",
                    "2. Naciśnij Enter po każdym upuszczonym pliku",
                    "3. Po zakończeniu naciśnij Enter jeszcze raz",
                ]
            ),
            [".pdf"],
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
            dir=True,
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


def convert_to_pdf(save=True):
    document_paths = multiple_files_input(
        "\n".join(
            [
                "1. Pojedynczo przeciągaj i upuszczaj pliki do konwersji tutaj",
                "  - Wspierane formaty: .doc, .docx, .odt, .odf",
                "2. Naciśnij Enter po każdym upuszczonym pliku",
                "3. Po zakończeniu naciśnij Enter jeszcze raz",
            ]
        ),
        [".doc", ".docx", ".odt", ".odf"],
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
                dir=True,
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
        os.path.join(output_dir, ".".join(doc.split("/")[-1].split(".")[:-1]) + ".pdf")
        for doc in document_paths
    ]
    return output_files


def convert_and_merge():
    converted_files = convert_to_pdf(save=False)

    if converted_files is None or len(converted_files) == 0:
        return press_enter_to_continue("Nie udało się skonwertować dokumentów do PDF")

    merge_pdfs(converted_files)


def pdfs_manager():
    clear_screen()
    last_selected = None

    while True:
        clear_screen()
        print("Witaj w menedżerze PDFów!")
        print("===========================================")

        options = []

        options.append({"label": "Wróć", "action": lambda: None})
        options.append({"label": "Połącz dokumenty PDF", "action": merge_pdfs})
        options.append(
            {"label": "Konwertuj dokumenty do PDF", "action": convert_to_pdf}
        )
        options.append(
            {
                "label": "Konwertuj dokumenty do PDF i połącz",
                "action": convert_and_merge,
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


def main():
    last_selected = None

    while True:
        shutdown_schedule_time = shutdown_scheduled_in_hours()
        plex_present = is_plex_present()
        plex_running = plex_present and is_plex_running()

        clear_screen()
        print_welcome_message()

        print("===========================================")
        if shutdown_schedule_time:
            print(f"Wyłączenie komputera zaplanowane na {shutdown_schedule_time}")
        if plex_present:
            print(f"Plex: {'ON' if plex_running else 'OFF'}")
        print("===========================================")

        options = []

        options.append({"label": "Wyjdź", "action": exit})

        if shutdown_schedule_time:
            options.append(
                {"label": "Anuluj wyłączenie komputera", "action": cancel_shutdown}
            )
        else:
            options.append(
                {"label": "Zaplanuj wyłączenie komputera", "action": schedule_shutdown}
            )

        if plex_present:
            if plex_running:
                options.append({"label": "Wyłącz Plex", "action": stop_plex})
            else:
                options.append({"label": "Włącz Plex", "action": start_plex})

        options.append({"label": "Pobierz napisy", "action": subtitles_downloader})
        options.append({"label": "Zainstaluj czcionki", "action": install_fonts})
        options.append({"label": "Zaktualizuj skrypt", "action": update_script})
        options.append({"label": "Zarządzaj PDFami", "action": pdfs_manager})

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
