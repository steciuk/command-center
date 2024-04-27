import os
import time

from utils import clear_screen


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
        # clear_screen()
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
