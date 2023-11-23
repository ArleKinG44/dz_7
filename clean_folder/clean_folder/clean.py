import os
import sys
import shutil
import re
from collections import defaultdict

# Функція для транслітерації й заміщення символів
def normalize(name):
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

    TRANS = {ord(c.upper()): l.upper() for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION)}
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()

    translate_name = "".join(TRANS.get(ord(c), c) for c in name)
    normalized_name = re.sub('[^a-zA-Z0-9]', '_', translate_name)

    return normalized_name

# Функція сортування 
def sort_files(start_path):
    extensions = {
        "images": ['.png', '.jpeg', '.jpg', '.svg'],
        "video": ['.avi', '.mp4', '.mov', '.mkv'],
        "documents": ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'],
        "audio": ['.mp3', '.ogg', '.wav', '.amr'],
        "archives": ['.zip', '.gz', '.tar'],
        "Eny_trash": []
    }

    ext_counter = defaultdict(list)

    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in extensions]

        for file in files:
            file_ext = os.path.splitext(file)[-1].lower()  # перетворення розширення файлу на нижній регістр
            moved = False

            for category, exts in extensions.items():
                if file_ext in exts:
                    shutil.move(os.path.join(root, file), os.path.join(start_path, category, file))
                    moved = True
                    ext_counter[category].append(file_ext)
                    break

            if not moved:
                shutil.move(os.path.join(root, file), os.path.join(start_path, "Eny_trash", file))
                ext_counter["Eny_trash"].append(file_ext)

    known_exts = set()
    unknown_exts = set()

    for category, exts in ext_counter.items():
        if category != "Eny_trash":
            known_exts.update(set(exts))
        else:
            unknown_exts.update(set(exts))

    print(f"Відомі розширення: {known_exts}")
    print(f"Невідомі розширення: {unknown_exts}")



# функція для нормалізації файлів
def process_files_norm(start_path):
    categories = ["images", "video", "documents", "audio"]
    all_files = {}

    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d in categories]

        for file in files:
            filename, file_ext = os.path.splitext(file)
            normalized_name = normalize(filename)
            new_file = normalized_name + file_ext

            if os.path.exists(os.path.join(root, new_file)):
                i = 1
                while os.path.exists(os.path.join(root, f"{normalized_name}_{i}{file_ext}")):
                    i += 1
                new_file = f"{normalized_name}_{i}{file_ext}"

            shutil.move(os.path.join(root, file), os.path.join(root, new_file))

            category = os.path.basename(root)
            if category not in all_files:
                all_files[category] = []
            all_files[category].append(new_file)

    for category, files in all_files.items():
        print(f"Category: {category}")
        for file in files:
            print(f"  {file}")



def unpack_archives(start_path):
    archives_folder = os.path.join(start_path, 'archives')
    for filename in os.listdir(archives_folder):
        file_path = os.path.join(archives_folder, filename)
        new_folder_path = os.path.join(archives_folder, os.path.splitext(filename)[0])
        os.makedirs(new_folder_path, exist_ok=True)
        try:
            shutil.unpack_archive(file_path, new_folder_path)
            os.remove(file_path)
        except Exception as e:
            print(f"Не вдалося розпакувати файл {filename}. Помилка: {e}")
            os.remove(file_path)



# Функція для видалення порожніх папок 
def remove_empty_folders(path):
    # check if the path is a directory
    if os.path.isdir(path):
        # get the list of all files and folders in the path
        contents = os.listdir(path)
        # if the directory is empty, remove it
        if not contents:
            os.rmdir(path)         
        else:
            # if the directory is not empty, check all subdirectories
            for item in contents:
                full_path = os.path.join(path, item)
                remove_empty_folders(full_path)
            # after removing subdirectories, check if the directory has become empty
            contents = os.listdir(path)
            if not contents:
                os.rmdir(path)

                           
def main():

    if len(sys.argv) == 2:
        folder = sys.argv[1]

        folders = ["images", "video", "documents", "audio", "archives", "Eny_trash"]

        for subfolder in folders:
            os.makedirs(os.path.join(folder, subfolder), exist_ok=True)

        sort_files(folder)
        process_files_norm(folder)
        unpack_archives(folder)
        remove_empty_folders(folder)

    else:
        print("Будь ласка, вкажіть ім'я папки як аргумент при запуску скрипта.")

if __name__ == "__main__":
    main()