import os

from utils import clear_screen


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
