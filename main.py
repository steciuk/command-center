#!/usr/bin/env python3
import os
import time

import cv2
from napi import NapiPy


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


def plex_is_running():
    return os.system("systemctl is-active --quiet plexmediaserver")


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

    print(f"FPS: {fps:.2f}")
    print(f"Czas trwania: {duration}")


def download_subtitles():
    clear_screen()
    movie_path = input("Przeciągnij i upuść tutaj plik filmu: ")
    movie_path = movie_path.strip("'")

    if not os.path.exists(movie_path):
        clear_screen()
        print("Podany plik nie istnieje.")
        input("Naciśnij Enter aby kontynuować...")
        return

    if os.path.isdir(movie_path):
        clear_screen()
        print("Podano folder zamiast pliku.")
        input("Naciśnij Enter aby kontynuować...")
        return

    clear_screen()
    try:
        display_movie_fps_and_duration(movie_path)
    except Exception as _:
        clear_screen()
        print("Podany plik najprawdopodobniej nie jest filmem.")
        input("Naciśnij Enter aby kontynuować...")
        return

    hash = input("\nPodaj hash napisów: ")
    hash = hash.strip()
    if hash.startswith("napiprojekt:"):
        hash = hash.split(":")[1]

    if len(hash) != 32:
        clear_screen()
        print("Podano nieprawidłowy hash.")
        print(f"+{hash}+")
        input("Naciśnij Enter aby kontynuować...")
        return

    try:
        napi = NapiPy()
        _, _, subtitles = napi.download_subs(hash)
        subs_path = napi.move_subs_to_movie(subtitles, movie_path)
    except Exception as _:
        clear_screen()
        print("Nie udało się pobrać napisów.")
        input("Naciśnij Enter aby kontynuować...")

    clear_screen()
    print(f"Pobrano napisy do: {subs_path}")
    input("Naciśnij Enter aby kontynuować...")


def main():
    last_selected = None

    while True:
        shutdown_schedule_time = shutdown_scheduled_in_hours()
        plex_running = plex_is_running()

        clear_screen()
        print("Cześć kochany Tatusiu! :*")

        print("===========================================")
        if shutdown_schedule_time:
            print(f"Wyłączenie komputera zaplanowane na {shutdown_schedule_time}")
        print(f"Plex: {'ON' if plex_running == 0 else 'OFF'}")
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

        if plex_running == 0:
            options.append({"label": "Wyłącz Plex", "action": stop_plex})
        else:
            options.append({"label": "Włącz Plex", "action": start_plex})

        options.append({"label": "Pobierz napisy", "action": download_subtitles})

        for i, option in enumerate(options):
            print(f"{i}. {option['label']}")

        last_selected = input("\nWybierz opcję: ")

        try:
            last_selected = int(last_selected)
            if last_selected < 0 or last_selected >= len(options):
                continue
        except ValueError:
            continue

        options[last_selected]["action"]()


if __name__ == "__main__":
    main()
