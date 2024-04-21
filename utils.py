import os


def clear_screen():
    os.system("clear")


def path_dnd_input(*prompts, is_dir=False, allow_empty=False):
    path = input("\n".join(prompts))
    path = path.strip().strip("'")

    if allow_empty and path == "":
        return path

    if is_dir:
        if not os.path.exists(path):
            raise FileNotFoundError("Podany folder nie istnieje")
        if not os.path.isdir(path):
            raise NotADirectoryError("Podano plik zamiast folderu")
    else:
        if not os.path.exists(path):
            raise FileNotFoundError("Podany plik nie istnieje")
        if os.path.isdir(path):
            raise IsADirectoryError("Podano folder zamiast pliku")

    return path


def press_enter_to_continue(message):
    clear_screen()
    print(message)
    input("Naciśnij Enter aby kontynuować...")


def multiple_files_input(*prompts, allowed_extensions=None):
    allowed_extensions = [] if allowed_extensions is None else allowed_extensions
    file_path = None
    file_paths = set()
    file_paths_in_order = []

    while file_path != "":
        clear_screen()
        print("\n".join(prompts))

        if len(file_paths_in_order) > 0:
            print("\nDodane pliki:")
            for file in file_paths_in_order:
                print(f"- {file.split('/')[-1]}")

        try:
            file_path = path_dnd_input("", "Plik: ", allow_empty=True, is_dir=False)
        except Exception as e:
            press_enter_to_continue(str(e))
            continue

        if file_path == "":
            break

        if len(allowed_extensions) > 0:
            if not any(file_path.endswith(ext) for ext in allowed_extensions):
                press_enter_to_continue(
                    f"Podany plik nie jest obsługiwanym plikiem: {', '.join(allowed_extensions)}"
                )
                continue

        if file_path in file_paths:
            press_enter_to_continue("Podany plik został już dodany")
            continue

        file_paths.add(file_path)
        file_paths_in_order.append(file_path)

    return file_paths_in_order
