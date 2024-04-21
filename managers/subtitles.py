import time
import cv2
from napi import NapiPy
from utils import clear_screen, path_dnd_input, press_enter_to_continue


class SubtitlesManager:
    def __init__(self):
        self.napi = NapiPy()

    def menu(self):
        clear_screen()
        print("Witaj w pobieraczu napisów!")
        print("===========================================")

        options = []

        options.append({"label": "Wróć", "action": lambda: None})
        options.append(
            {
                "label": "Pobierz napisy automatycznie",
                "action": self.download_subtitles_auto,
            }
        )
        options.append(
            {
                "label": "Pobierz napisy ręcznie",
                "action": self.download_subtitles_manual,
            }
        )

        for i, option in enumerate(options):
            print(f"{i}. {option['label']}")

        last_selected = input("\nWybierz opcję i naciśnij Enter: ")

        try:
            last_selected = int(last_selected)
            if last_selected <= 0 or last_selected >= len(options):
                return
        except ValueError:
            return

        try:
            options[last_selected]["action"]()
        except Exception as e:
            press_enter_to_continue(f"{str(e)}\n\nWystąpił krytyczny błąd")

    def display_movie_fps_and_duration(self, path):
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        duration = frame_count / fps
        duration = time.strftime("%H:%M:%S", time.gmtime(duration))

        print(f"FPS: {fps:.3f}")
        print(f"Czas trwania: {duration}")

    def download_subtitles_auto(self):
        clear_screen()

        try:
            movie_path = path_dnd_input(
                "1. Przeciągnij i upuść tutaj plik filmu",
                "2. Naciśnij Enter",
                "",
                "Plik: ",
                is_dir=False,
            )
        except Exception as e:
            return press_enter_to_continue(str(e))

        subs_hash = self.napi.calc_hash(movie_path)

        _, _, subtitles = self.napi.download_subs(subs_hash)

        if subtitles:
            self.napi.move_subs_to_movie(subtitles, movie_path)
            return press_enter_to_continue("Poprawnie pobrano napisy!")

        clear_screen()
        print("Nie udało się dopasować napisów automatycznie, spróbuj ręcznie\n")
        self.download_subtitles_manual(movie_path)

    def download_subtitles_manual(self, movie_path=None):
        if movie_path is None:
            clear_screen()

            try:
                movie_path = path_dnd_input(
                    "1. Przeciągnij i upuść tutaj plik filmu",
                    "2. Naciśnij Enter",
                    "",
                    "Plik: ",
                    is_dir=False,
                )
            except Exception as e:
                return press_enter_to_continue(str(e))

            clear_screen()

        try:
            self.display_movie_fps_and_duration(movie_path)
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

        subs_hash = input("Hash: ")
        subs_hash = subs_hash.strip()
        if subs_hash.startswith("napiprojekt:"):
            subs_hash = subs_hash.split(":")[1]

        if len(subs_hash) != 32:
            return press_enter_to_continue("Podano niepoprawny hash")

        _, _, subtitles = self.napi.download_subs(subs_hash)

        if subtitles:
            self.napi.move_subs_to_movie(subtitles, movie_path)
            return press_enter_to_continue("Poprawnie pobrano napisy!")

        return press_enter_to_continue("Nie udało się pobrać napisów")
