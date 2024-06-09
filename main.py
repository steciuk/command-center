#!/usr/bin/env python3
from managers.fonts import FontManager
from managers.pdf import PdfManager
from managers.plex import PlexManager
from managers.script import ScriptGitUpdater
from managers.shutdown import ShutdownManager
from managers.subtitles import SubtitlesManager
from menu import Menu


def main():
    shutdown_manager = ShutdownManager()
    plex_manager = PlexManager()
    subtitles_downloader = SubtitlesManager()
    pdfs_manager = PdfManager()
    script_updater = ScriptGitUpdater()
    fonts_manager = FontManager()

    menu = Menu()
    menu.with_header("Witaj! Jak mogę dzisiaj pomóc?").with_header(
        "===========================================",
        lambda: plex_manager.plex_present or shutdown_manager.scheduled,
    ).with_header(
        lambda: f"Zaplanowane wyłączenie: {shutdown_manager.scheduled}",
        lambda: shutdown_manager.scheduled,
    ).with_header(
        lambda: f"Plex: {'ON' if plex_manager.plex_running else 'OFF'}",
        lambda: plex_manager.plex_present,
    ).with_action(
        "Zaplanuj wyłączenie komputera",
        shutdown_manager.schedule_shutdown,
        lambda: not shutdown_manager.scheduled,
    ).with_action(
        "Anuluj wyłączenie komputera",
        shutdown_manager.cancel_shutdown,
        lambda: shutdown_manager.scheduled,
    ).with_submenu(
        "Pobierz napisy", subtitles_downloader.menu
    ).with_submenu(
        "Zarządzaj czcionkami", fonts_manager.menu
    ).with_submenu(
        "Zarządzaj PDFami", pdfs_manager.menu
    ).with_action(
        "Wyłącz Plex",
        plex_manager.stop_plex,
        lambda: plex_manager.plex_present and plex_manager.plex_running,
    ).with_action(
        "Włącz Plex",
        plex_manager.start_plex,
        lambda: plex_manager.plex_present and not plex_manager.plex_running,
    ).with_submenu(
        "Zaktualizuj skrypt", script_updater.menu
    ).with_exit()

    menu.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
