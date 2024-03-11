#!/usr/bin/env python3
import os
import time


def clear_screen():
    os.system("clear")


def schedule_shutdown():
    clear_screen()
    num_hours = input("Za ile godzin wyłączyć komputer? (0 - wróć): ")
    try:
        num_hours = int(num_hours)
        if num_hours < 0:
            print("Podaj dodatnią liczbę godzin")
            return
    except ValueError:
        print("Podaj poprawną liczbę godzin")
        return

    if num_hours == 0:
        return

    os.system(f"shutdown +{num_hours * 60}")


def cancel_shutdown():
    os.system("shutdown -c")


def plex_is_running():
    return os.system("systemctl is-active --quiet plexmediaserver")


def start_plex():
    os.system("sudo systemctl start plexmediaserver")


def stop_plex():
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

        for i, option in enumerate(options):
            print(f"{i + 1}. {option['label']}")

        print("q. Wyjdź\n")

        last_selected = input("Wybierz opcję: ")

        if last_selected == "q":
            exit()

        try:
            last_selected = int(last_selected)
            if last_selected < 1 or last_selected > len(options):
                continue
        except ValueError:
            continue

        options[last_selected - 1]["action"]()


if __name__ == "__main__":
    main()
