import os
import shutil

from typing import Union
from datetime import datetime

APP_STATE_FILE_NAME = "app_state"
DATA_FILE_NAME = "data"
HISTORY_FOLDER_NAME = "historial"
NOTIFICATION_ENERGY_USAGE = 0.0000025


def update_app_state(entries: list[list[str]]):
    """
    Función principal para manejar el estado de la app y actualización de los datos.
    Itera todas las apps para actualizar su fecha de 'última vez abierta' y luego se
    pasa las entradas a entry_handler para que actualice los valores de las notificaciones
    """
    # Leemos todas las líneas del archivo actual o lo cremos en caso de no existir
    try:
        with open(APP_STATE_FILE_NAME + ".txt", "r+") as file:
            current_lines = file.readlines()
    except FileNotFoundError:
        current_lines = [
            "# Archivo de datos manejado por NO MOLESTAPP. No modificarlos manualmente\n",
            "# app,status,last_updated\n",
        ]

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Creamos una lista solo con los nombres de las apps a actualizar
    updated_apps = [entry[0] for entry in entries]
    updated_lines = []

    # Iteramos línea por línea y si la app ya existía, actualizamos su fecha
    # o generamos una nueva línea para aquellas que no estén
    for line in current_lines:
        if line.strip().startswith("#"):
            updated_lines.append(line)
            continue

        row = line.strip().split(",")
        app_name = row[0]

        if app_name in updated_apps:
            status = row[1]
            updated_line = f"{app_name},{status},{current_date}\n"
            updated_lines.append(updated_line)
            updated_apps.remove(app_name)
        else:
            updated_lines.append(line)

    for app_name in updated_apps:
        new_line = f"{app_name},active,{current_date}\n"
        updated_lines.append(new_line)

    with open(APP_STATE_FILE_NAME + ".txt", "w") as file:
        file.writelines(updated_lines)

    entry_handler(entries)


def get_app_used_percentage(requested_app: str) -> float:
    notifications_count: int = 0
    opened_count: int = 0

    if os.path.exists(HISTORY_FOLDER_NAME):
        history_files = os.listdir(HISTORY_FOLDER_NAME)

        for file in history_files:
            direccion = os.path.join(HISTORY_FOLDER_NAME, file)

            with open(direccion, "r+") as file:
                for line in file:
                    if line.strip().startswith("#"):
                        continue
                    else:
                        file_app_name, file_notif_count, file_open_count = line.split(
                            ","
                        )

                        if file_app_name == requested_app:
                            notifications_count += int(file_notif_count)
                            opened_count += int(file_open_count)

    if os.path.exists(DATA_FILE_NAME + ".txt"):
        with open(DATA_FILE_NAME + ".txt", "r+") as file:
            for line in file:
                if line.strip().startswith("#"):
                    continue
                else:
                    file_app_name, file_notif_count, file_open_count = line.split(",")

                    if file_app_name == requested_app:
                        notifications_count += int(file_notif_count)
                        opened_count += int(file_open_count)

    if notifications_count:
        used_percentage = opened_count * 100 / notifications_count
        return used_percentage
    else:
        return 0


def get_active_apps() -> Union[list[tuple[str, str, datetime]], None]:
    try:
        active_apps = []

        with open(APP_STATE_FILE_NAME + ".txt", "r+") as file:
            for line in file:
                if line.strip().startswith("#"):
                    continue
                else:
                    row = line.strip().split(",")
                    app_name = row[0]
                    status = row[1]

                    if status == "active":
                        year, month, day = row[2].split("-")
                        last_updated = datetime(int(year), int(month), int(day))

                        active_apps.append((app_name, status, last_updated))

        return active_apps
    except FileNotFoundError:
        return None


# def get_apps_notif_average() -> list[tuple[str, float]]:
#     notifications_overview = []


def silence_app(requested_app: str):
    try:
        with open(APP_STATE_FILE_NAME + ".txt", "r+") as file:
            current_lines = file.readlines()
    except FileNotFoundError:
        raise ValueError("App no encontrada")

    found_app = False
    updated_lines = []

    for line in current_lines:
        if line.strip().startswith("#"):
            updated_lines.append(line)
            continue

        row = line.strip().split(",")
        app_name = row[0]

        if app_name.lower() == requested_app:
            file_date = row[2]
            updated_line = f"{app_name},muted,{file_date}\n"
            updated_lines.append(updated_line)
            found_app = True
        else:
            updated_lines.append(line)

    if not found_app:
        raise ValueError("App no encontrada")

    with open(APP_STATE_FILE_NAME + ".txt", "w") as file:
        file.writelines(updated_lines)


def entry_handler(entries: list[list[str]]):
    file_name = DATA_FILE_NAME + ".txt"
    file_exists = os.path.exists(file_name)
    mes_actual = datetime.now().strftime("%B")

    if file_exists:
        file_month = read_file_month(file_name)

        if file_month == mes_actual:
            write_entries(entries)
        else:
            if not os.path.exists(HISTORY_FOLDER_NAME):
                os.makedirs(HISTORY_FOLDER_NAME)

            destino = os.path.join(HISTORY_FOLDER_NAME, file_month + ".txt")

            shutil.move(file_name, destino)
    else:
        create_file(DATA_FILE_NAME)
        write_entries(entries)


def write_entries(entries: list[list[str]]):
    file_name = DATA_FILE_NAME + ".txt"

    with open(file_name, "a") as file:
        for row in entries:
            file.write(f"{','.join(row)}\n")


def read_enties(month: str) -> list[list[str]]:
    file_name = month.lower() + ".txt"
    folder_name = "historial"
    file_location = os.path.join(folder_name, file_name)

    if os.path.exists(file_location):
        entries = []

        with open(file_location, "r+") as file:
            for line in file:
                if line.startswith("# "):
                    continue
                else:
                    line = line.strip().split(",")
                    entries.append(line)

        return entries
    else:
        raise ValueError(f"No existe un archivo para el mes {month}")


def read_file_month(path: str) -> str:
    month = ""

    try:
        with open(path, "r+") as file:
            for line in file:
                if line.startswith("# "):
                    month = line.strip().replace("# ", "").lower()
                    print(f"Mes encontrado: {month}")

                    return month
    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo no encontrado en ruta: {path}")
    finally:
        return month


def read_month(month: str) -> list[tuple[str, int, int]]:
    path = os.path.join(HISTORY_FOLDER_NAME, month + ".txt")
    data = []

    with open(path, "r+") as file:
        for line in file:
            if line.startswith("# "):
                continue
            else:
                app_name, found_notif, found_useful = line.split(",")

                app_exists = False
                for i, (key, notif_count, useful_count) in enumerate(data):
                    if app_name == key:
                        app_exists = True
                        new_notif_count = int(found_notif) + notif_count
                        new_useful_count = int(found_useful) + useful_count

                        data[i] = (key, new_notif_count, new_useful_count)

                if not app_exists:
                    data.append((app_name, int(found_notif), int(found_useful)))

    return data


def create_file(file_name: str, path: str | None = None):
    if path:
        direction = os.path.join(path, file_name + ".txt")
    else:
        direction = file_name + ".txt"

    with open(direction, "w") as file:
        if file_name == DATA_FILE_NAME:
            current_month = datetime.now().strftime("%B")
            file.write(f"# {current_month.capitalize()}\n")


if __name__ == "__main__":
    print("no function assigned")
