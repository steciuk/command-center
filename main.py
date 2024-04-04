#!/usr/bin/env python3
import os
import time

import cv2
from napi import NapiPy
import pwd


def clear_screen():
    os.system("clear")


def schedule_shutdown():
    clear_screen()
    num_hours = input("Za ile godzin wyłączyć komputer? (0 - wróć): ")
    try:
        num_hours = int(num_hours)
        if num_hours < 0:
            return
    except ValueError:
        return

    if num_hours == 0:
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


def secods_to_hh_mm_ss(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def display_movie_fps_and_duration(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    duration = frame_count / fps

    duration = secods_to_hh_mm_ss(duration)

    print(f"FPS: {fps:.3f}")
    print(f"Czas trwania: {duration}")


def download_subtitles():
    clear_screen()
    print("1. Przeciągnij i upuść tutaj plik filmu")
    print("2. Naciśnij Enter")
    movie_path = input("\nPlik: ")
    movie_path = movie_path.strip()
    movie_path = movie_path.strip("'")

    if not os.path.exists(movie_path):
        clear_screen()
        print("Podany plik nie istnieje")
        input("Naciśnij Enter aby kontynuować...")
        return

    if os.path.isdir(movie_path):
        clear_screen()
        print("Podano folder zamiast pliku")
        input("Naciśnij Enter aby kontynuować...")
        return

    clear_screen()
    try:
        display_movie_fps_and_duration(movie_path)
    except Exception as _:
        clear_screen()
        print("Podany plik najprawdopodobniej nie jest filmem, bądź jest uszkodzony")
        input("Naciśnij Enter aby kontynuować...")
        return

    print("\n1. Wejdź na stronę https://www.napiprojekt.pl/napisy-szukaj")
    print("2. Wyszukaj film po tytule i wybierz pasujący wynik (https://imgur.com/a/yIAA3zG)")
    print("  - Upewnij się, że tytuł i rok filmu są zgodne z tymi z pliku")
    print("  - Jeśli nie ma wyników, spróbuj wyszukać po angielskim (lub polskim) tytule")
    print("  - Czasem po wybraniu wyniku napiprojekt otwiera nową stronę z reklamą,")
    print("    wtedy wróć do poprzedniej strony i ponów próbę wybrania wyniku")
    print("3. Kliknij przycisk 'napisy' (https://imgur.com/a/k2fVPjo)")
    print("4. Dopasuj napisy do czasu trwania i FPS filmu (https://imgur.com/a/GR0Hw1z)")
    print("  - Najłatwiej posortować wyniki po czasie trwania,")
    print("    klikając w nagłówek kolumny 'CZAS TRWANIA'")
    print("  - Jeśli jest kilka pasujących wyników, wybierz ten z największą ilością pobrań")
    print("5. Kliknij prawym przyciskiem myszy na nazwę pliku i wybierz 'Kopiuj odnośnik' (https://imgur.com/a/fPSGycC)")
    print("6. Wklej skopiowany hash poniżej (CTRL+SHIFT+V) i naciśnij Enter")
    print("  - Hash powinien wyglądać tak: 'napiprojekt:1234567890abcdef1234567890abcdef'")

    hash = input("\nHash: ")
    hash = hash.strip()
    if hash.startswith("napiprojekt:"):
        hash = hash.split(":")[1]

    if len(hash) != 32:
        clear_screen()
        print("Podano nieprawidłowy hash")
        input("Naciśnij Enter aby kontynuować...")
        return

    try:
        napi = NapiPy()
        _, _, subtitles = napi.download_subs(hash)
        subs_path = napi.move_subs_to_movie(subtitles, movie_path)
    except Exception as _:
        clear_screen()
        print("Nie udało się pobrać napisów")
        input("Naciśnij Enter aby kontynuować...")

    clear_screen()
    print("Poprawnie pobrano napisy!")
    input("Naciśnij Enter aby kontynuować...")


def print_welcome_message():
    usr = pwd.getpwuid(os.getuid())[0]

    match usr:
        case "tata":
            print("Cześć kochany Tatusiu! :*")
        case "ula":
            print("Cześć kochana Mamusiu! :*")
        case _:
            print(f"Witaj {usr}!")
            

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
