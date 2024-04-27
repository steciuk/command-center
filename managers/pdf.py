import os

from pypdf import PdfMerger

from menu import Menu
from utils import (
    clear_screen,
    multiple_files_input,
    path_dnd_input,
    press_enter_to_continue,
)


class PdfManager:
    def __init__(self):
        self.menu = (
            Menu()
            .with_header("Witaj w menedżerze PDFów!")
            .with_return()
            .with_action("Połącz dokumenty PDF", self.merge_pdfs)
            .with_action("Konwertuj dokumenty do PDF", self.convert_to_pdf)
            .with_action("Konwertuj dokumenty do PDF i połącz", self.convert_and_merge)
        )

    def merge_pdfs(self, document_paths=None):
        if document_paths is None:
            document_paths = multiple_files_input(
                "1. Pojedynczo przeciągaj i upuszczaj pliki do połączenia tutaj",
                "  - Wspierane formaty: .pdf",
                "2. Naciśnij Enter po każdym upuszczonym pliku",
                "3. Po zakończeniu naciśnij Enter jeszcze raz",
                allowed_extensions=[".pdf"],
            )

            if len(document_paths) == 0:
                return press_enter_to_continue("Nie wybrano żadnych dokumentów")

        clear_screen()
        try:
            output_path = path_dnd_input(
                "1. Przeciągnij i upuść folder, do którego ma być zapisany plik PDF",
                "2. Naciśnij Enter",
                "",
                "Folder: ",
                is_dir=True,
            )
        except Exception as e:
            return press_enter_to_continue(str(e))

        clear_screen()
        file_name = input("Podaj nazwę pliku wyjściowego: ")
        file_name = file_name.strip()
        if file_name == "":
            return press_enter_to_continue("Nie podano nazwy pliku wyjściowego")

        if not file_name.endswith(".pdf"):
            file_name += ".pdf"

        merger = PdfMerger()
        for document_path in document_paths:
            merger.append(document_path)

        merger.write(os.path.join(output_path, file_name))
        merger.close()

        press_enter_to_continue("Poprawnie połączono dokumenty w jeden plik PDF!")

    def convert_to_pdf(self, save=True):
        document_paths = multiple_files_input(
            "1. Pojedynczo przeciągaj i upuszczaj pliki do konwersji tutaj",
            "  - Wspierane formaty: .doc, .docx, .odt, .odf",
            "2. Naciśnij Enter po każdym upuszczonym pliku",
            "3. Po zakończeniu naciśnij Enter jeszcze raz",
            allowed_extensions=[".doc", ".docx", ".odt", ".odf"],
        )

        if len(document_paths) == 0:
            return press_enter_to_continue("Nie wybrano żadnych dokumentów")

        if save:
            clear_screen()
            try:
                output_dir = path_dnd_input(
                    "1. Przeciągnij i upuść folder, do którego mają być zapisane pliki PDF",
                    "2. Naciśnij Enter",
                    "",
                    "Folder: ",
                    is_dir=True,
                )
            except Exception as e:
                return press_enter_to_continue(str(e))
        else:
            output_dir = "/tmp/command_center"

        clear_screen()
        try:
            escaped_document_paths = [f"'{doc}'" for doc in document_paths]
            command = f"lowriter --convert-to pdf {' '.join(escaped_document_paths)} --outdir '{output_dir}'"
            os.system(command)
        except Exception as e:
            return press_enter_to_continue(str(e))

        if save:
            press_enter_to_continue("Poprawnie skonwertowano dokumenty do PDF!")

        output_files = [
            os.path.join(
                output_dir, ".".join(doc.split("/")[-1].split(".")[:-1]) + ".pdf"
            )
            for doc in document_paths
        ]
        return output_files

    def convert_and_merge(self):
        converted_files = self.convert_to_pdf(save=False)

        if converted_files is None or len(converted_files) == 0:
            return

        self.merge_pdfs(converted_files)
