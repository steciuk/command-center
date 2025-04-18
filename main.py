#!/usr/bin/env python3
from managers.fonts import FontManager
from managers.pdf import PdfManager
from managers.script import ScriptGitUpdater
from managers.shutdown import ShutdownManager
from managers.subtitles import SubtitlesManager
from menu import Menu


def main():
    shutdown_manager = ShutdownManager()
    subtitles_manager = SubtitlesManager()
    pdfs_manager = PdfManager()
    script_updater = ScriptGitUpdater()
    fonts_manager = FontManager()

    menu = Menu()
    menu.with_header("Witaj! Jak mogę dzisiaj pomóc?").with_header(
        "===========================================",
        lambda: shutdown_manager.scheduled,
    ).with_header(
        lambda: f"Zaplanowane wyłączenie: {shutdown_manager.scheduled}",
        lambda: shutdown_manager.scheduled,
    ).with_action(
        "Zaplanuj wyłączenie komputera",
        shutdown_manager.schedule_shutdown,
        lambda: not shutdown_manager.scheduled,
    ).with_action(
        "Anuluj wyłączenie komputera",
        shutdown_manager.cancel_shutdown,
        lambda: shutdown_manager.scheduled,
    ).with_submenu(
        "Zarządzaj napisami", subtitles_manager.menu
    ).with_submenu(
        "Zarządzaj czcionkami", fonts_manager.menu
    ).with_submenu(
        "Zarządzaj PDFami", pdfs_manager.menu
    ).with_submenu(
        "Zaktualizuj skrypt", script_updater.menu
    ).with_exit()

    menu.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
