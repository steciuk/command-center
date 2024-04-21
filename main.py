#!/usr/bin/env python3
from managers.pdf import PdfManager
from managers.plex import PlexManager
from managers.script import ScriptUpdater
from managers.shutdown import ShutdownManager
from managers.subtitles import SubtitlesManager
from managers.fonts import FontManager

from utils import clear_screen, press_enter_to_continue


def main():
    shutdown_manager = ShutdownManager()
    plex_manager = PlexManager()
    subtitles_downloader = SubtitlesManager()
    pdfs_manager = PdfManager()
    script_updater = ScriptUpdater()
    fonts_manager = FontManager()

    while True:
        clear_screen()
        print("Witaj! Jak mogę dzisiaj pomóc?")
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
        options.append(
            {"label": "Zainstaluj czcionki", "action": fonts_manager.install_fonts}
        )
        options.append(
            {"label": "Zaktualizuj skrypt", "action": script_updater.update_script}
        )
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
