#!/usr/bin/env python3
import os
import time
import pwd

import cv2
from napi import NapiPy


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


def download_subtitles():
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

    _, _, subtitles = napi.download_subs(hash)

    if subtitles:
        napi.move_subs_to_movie(subtitles, movie_path)
        return press_enter_to_continue("Poprawnie pobrano napisy!")

    press_enter_to_continue("Nie udało się pobrać napisów")


def print_welcome_message():
    usr = pwd.getpwuid(os.getuid())[0]

    match usr:
        case "tata":
            print("Cześć kochany Tatusiu! :*")
        case "ula":
            print("Cześć kochana Mamusiu! :*")
        case _:
            print(f"Witaj {usr}!")


def install_fonts():
    font_path = None
    font_paths = set()

    while font_path != "":
        clear_screen()
        print(
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
            )
        )

        if len(font_paths) > 0:
            print("\nDodane czcionki:")
            for font in font_paths:
                print(f"- {font.split('/')[-1]}")

        try:
            font_path = path_dnd_input(
                "", "Plik czcionki: ", allow_empty=True, dir=False
            )
        except Exception as e:
            press_enter_to_continue(str(e))
            continue

        if font_path == "":
            break

        if not font_path.endswith(".ttf") and not font_path.endswith(".otf"):
            press_enter_to_continue(
                "Podany plik nie jest obsługiwanymi czcionkami .ttf lub .otf"
            )
            continue

        font_paths.add(font_path)

    if len(font_paths) == 0:
        return press_enter_to_continue("Nie wybrano żadnych czcionek")

    otfs = [font for font in font_paths if font.endswith(".otf")]
    ttfs = [font for font in font_paths if font.endswith(".ttf")]

    if len(otfs) > 0:
        clear_screen()
        os.system("sudo mkdir -p /usr/share/fonts/opentype/installed")
        for otf in otfs:
            os.system(f"sudo cp -n {otf} /usr/share/fonts/opentype/installed/")

    if len(ttfs) > 0:
        clear_screen()
        os.system("sudo mkdir -p /usr/share/fonts/truetype/installed")
        for ttf in ttfs:
            os.system(f"sudo cp -n {ttf} /usr/share/fonts/truetype/installed/")

    clear_screen()
    os.system("sudo fc-cache -f -v")

    press_enter_to_continue(
        "Zainstalowano wybrane czcionki! Możesz usunąć pobrane pliki czcionek"
    )


def update_script():
    SCRIPT_PATH = os.path.dirname(__file__)
    PYTHON_PATH = os.path.join(SCRIPT_PATH, ".venv/bin/python3")

    clear_screen()
    requirements_path = path_dnd_input(
        "1. Żeby zaktualizować skrypt, potrzebny jest plik 'main.py' oraz opcjonalnie 'requirements.txt'",
        "2. Jeśli posiadasz plik 'requirements.txt', przeciągnij i upuść go tutaj i naciśnij Enter, w przeciwnym wypadku po prostu naciśnij Enter",
        "",
        "Plik: ",
        dir=False,
        allow_empty=True,
    )

    if requirements_path != "":
        if not requirements_path.endswith("requirements.txt"):
            return press_enter_to_continue(
                "Podany plik nie jest plikiem 'requirements.txt'"
            )

        clear_screen()
        os.system(f"{PYTHON_PATH} -m pip install -r {requirements_path}")

    clear_screen()
    main_path = path_dnd_input(
        "1. Przeciągnij i upuść plik 'main.py' tutaj",
        "2. Naciśnij Enter",
        dir=False,
    )

    if not main_path.endswith("main.py"):
        return press_enter_to_continue("Podany plik nie jest plikiem 'main.py'")

    os.system(f"cp {main_path} {SCRIPT_PATH}")

    press_enter_to_continue("Zaktualizowano skrypt!\nUruchom skrypt ponownie")
    exit()


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

        options.append({"label": "Pobierz napisy", "action": download_subtitles})
        options.append({"label": "Zainstaluj czcionki", "action": install_fonts})
        options.append({"label": "Zaktualizuj skrypt", "action": update_script})

        for i, option in enumerate(options):
            print(f"{i}. {option['label']}")

        last_selected = input("\nWybierz opcję i naciśnij Enter: ")

        try:
            last_selected = int(last_selected)
            if last_selected < 0 or last_selected >= len(options):
                continue
        except ValueError:
            continue

        options[last_selected]["action"]()


if __name__ == "__main__":
    main()
