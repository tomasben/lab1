import locale
import sys
import cli
import file
import os

from typing import Union
from cli import left_margin
from datetime import datetime


def main():
    locale.setlocale(locale.LC_ALL, "es_AR")

    while True:
        cli.clear()
        cli.draw_heading(text="NO MOLESTAPP", width=60)
        print_energy_saving(width=60)

        print(f"\n{left_margin}ACCIONES: ")
        print(f"{left_margin + '  '}[1] Ingresar una nueva entrada")
        print(f"{left_margin + '  '}[2] Generar reporte mensual")
        print(f"{left_margin + '  '}[3] Ver recomendaciones")
        print(f"\n{left_margin + '  '}[4] Salir")

        choice = input(f"\n{left_margin}► Ingrese su elección [1-4]: ")

        match choice:
            case "1":
                new_entry()
            case "2":
                monthly_report()
            case "3":
                advices_menu()
            case "4":
                cli.clear()
                sys.exit(0)


def print_energy_saving(width: int):
    NOTIF_ENERGY_CONSUMPTION = 0.25
    active_apps_data = file.get_active_apps()
    energy_saved = 0

    if active_apps_data:
        active_apps = [app[0] for app in active_apps_data]

        for app in active_apps:
            notif_avergage = file.get_app_notif_average(app)

            if notif_avergage:
                energy_saved += notif_avergage * NOTIF_ENERGY_CONSUMPTION

    if energy_saved > 0:
        # Estimado de porcentaje de carga relativo a una bateria de 4000mAh
        estimate = round(energy_saved / 15400 * 100, 2)

        print(f"\n{left_margin}Desde que empezaste a usar NO MOLESTAPP ahorraste:\n")
        print(f"{left_margin}{f'⚡ {estimate}% de carga ⚡'.center(width)}\n")


def new_entry():
    date = datetime.now().strftime("%a, %d del %Y")
    data: list[list[str]] = []
    formatted_data = []

    while True:
        cli.clear()

        if len(data) > 0:
            formatted_data = format_apps_view(data)

        cli.draw_primary_box(heading=f"Nueva entrada - {date}", content=formatted_data)

        print(f"\n{left_margin}ACCIONES: ")
        print(f"{left_margin + '  '}• para AÑADIR: ingrese el nombre de la app")
        print(f"{left_margin + '  '}• para FINALIZAR: pulse ENTER")
        print(f"{left_margin + '  '}• para CANCELAR: escriba 'salir'")

        choice = handle_input(
            valid_num_range=None, admits_text=True, admits_emty_string=True
        )

        match choice:
            case "salir":
                break
            case "":
                if len(data) > 0:
                    file.update_app_state(data)
                break
            case _:
                app = handle_entry(choice)
                data.append(app)


def monthly_report():
    box_width = 50
    cli.clear()
    cli.draw_heading("Historial", width=box_width)

    folder_exists = os.path.exists("historial")

    if folder_exists:
        history_files = os.listdir("historial")

        for index, f in enumerate(history_files, start=1):
            month = f.replace(".txt", "")

            month_data = file.read_month(month)
            notifications_count = sum([app[1] for app in month_data])

            formatted_data = [
                f"Contenido: {len(month_data)} Aplicaciones & {notifications_count} Notificaciones"
            ]
            cli.draw_secondary_box(
                content=formatted_data,
                heading=f"{index}. {month.capitalize()}",
            )

        print(f"\n{left_margin}ACCIONES:")
        print(
            f"{left_margin + '  '}• para VER: ingrese el número del mes [{1}-{len(history_files)}]"
        )
        print(f"{left_margin + '  '}• para SALIR: presione ENTER")

        while True:
            choice = handle_input(
                valid_num_range=(1, len(history_files)),
                admits_text=True,
                admits_emty_string=True,
            )

            if choice.isdigit():
                num = int(choice)
                chosen_month = history_files[num - 1].replace(".txt", "")

                month_view(chosen_month)
                break
            elif choice == "":
                break
    else:
        print(f"\n{left_margin}No hay entradas recientes.")
        input(f"\n{left_margin}Presione ENTER para salir... ")


def advices_menu():
    while True:
        cli.clear()
        active_apps = file.get_active_apps()

        if active_apps:
            formatted_data = format_advices_data(active_apps)
        else:
            formatted_data = []

        cli.draw_primary_box(heading="Recomendaciones", content=formatted_data)

        print(f"\n{left_margin}ACCIONES:")
        print(
            f"{left_margin + '  '}• para SILENCIAR: ingrese el nombre de la aplicación"
        )
        print(f"{left_margin + '  '}• para SALIR: presione ENTER")

        choice = handle_input(
            valid_num_range=None,
            admits_text=True,
            admits_emty_string=True,
        )

        if choice == "":
            break
        else:
            try:
                file.silence_app(choice)
            except ValueError:
                continue


def format_advices_data(data: list[tuple[str, str, datetime]]) -> list[str]:
    labels = [" # ", " APLICACIÓN ", " ULT. VEZ ABIERTO ", " RECOMENDACIÓN "]
    spacing = "   "
    formatted_data = []

    header_widths = [len(i) for i in labels]
    for row in data:
        for i, cell in enumerate(row, start=1):
            header_widths[i] = max(header_widths[i], len(str(cell)))

    header_parts = []
    for k, part in enumerate(labels):
        header_parts.append(part.center(header_widths[k]))

    header_line = spacing.join(header_parts)
    formatted_data.append(header_line)

    separator = spacing.join(["─" * len for len in header_widths])
    formatted_data.append(separator)

    for i, row in enumerate(data, start=1):
        current_date = datetime.now()

        enumerated_row = list(row)
        enumerated_row.insert(0, str(i) + ".")

        data_parts = []
        for j, cell in enumerate(enumerated_row):
            match j:
                case 0:
                    cell = str(cell)
                    data_parts.append(cell.center(header_widths[0]))
                case 1:
                    cell = str(cell)
                    data_parts.append(cell.capitalize().ljust(header_widths[1]))
                case 3:
                    if isinstance(cell, datetime):
                        date_delta = current_date - cell
                        data_parts.append(
                            f"{date_delta.days} días".center(header_widths[2])
                        )

        percentage = file.get_app_used_percentage(str(enumerated_row[1]))
        if percentage <= 40.0:
            data_parts.append("🟠 Silenciar".ljust(header_widths[3]))
        else:
            data_parts.append("🟢 Mantener".ljust(header_widths[3]))

        data_line = spacing.join(data_parts)
        formatted_data.append(data_line)

    return formatted_data


def month_view(month: str):
    cli.clear()
    data = file.read_enties(month)

    formatted_data = format_apps_view(data)

    cli.draw_primary_box(
        content=formatted_data, heading=f"Reporte mensual: {month.capitalize()}"
    )

    input(f"\n{left_margin}► Presione ENTER para volver...")


def handle_entry(app_name: str) -> list[str]:
    app = [app_name.lower()]

    quantity = handle_input(
        valid_num_range=(1, float("inf")),
        admits_text=False,
        prompt="Ingrese el número de notificaciones: ",
    )
    app.append(quantity)

    useful_notifs = handle_input(
        valid_num_range=(0, int(quantity)),
        admits_text=False,
        prompt="Ingrese cuántas de ellas abrió: ",
    )
    app.append(useful_notifs)

    return app


def format_apps_view(data: list[list[str]]) -> list[str]:
    headers = [" # ", " APLICACIÓN ", " NOTIFICACIONES ", " ABIERTAS ", " % ABIERTAS "]
    spacing = "   "
    formatted_data = []

    headers_widths = [len(h) for h in headers]
    for row in data:
        for j, cell in enumerate(row, start=1):
            headers_widths[j] = max(headers_widths[j], len(cell))

    header_parts = []
    for i, header in enumerate(headers):
        header_parts.append(header.center(headers_widths[i]))

    header_line = spacing.join(header_parts)
    formatted_data.append(header_line)

    separator = spacing.join(["─" * len for len in headers_widths])
    formatted_data.append(separator)

    for i, row in enumerate(data, start=1):
        enumerated_row = list(row)
        enumerated_row.insert(0, str(i))
        data_parts = []

        for j, cell in enumerate(enumerated_row):
            if j == 1:
                data_parts.append(cell.capitalize().ljust(headers_widths[1]))
            else:
                data_parts.append(cell.center(headers_widths[j]))

        opened_percent = (
            str(round(int(enumerated_row[3]) * 100 / int(enumerated_row[2]))) + "%"
        )
        data_parts.append(opened_percent.center(headers_widths[4]))

        data_line = spacing.join(data_parts)
        formatted_data.append(data_line)

    return formatted_data


def handle_input(
    valid_num_range: Union[tuple[float, float], None],
    admits_text: bool,
    prompt: str = "► ",
    admits_emty_string: bool = False,
) -> str:
    """
    Función para manejar de manera global el input del usuario, especificando
    el rango de números aceptados y si los valores alfanuméricos o vacíos (ENTER)
    son aceptados o no en un determinado momento.
    """
    while True:
        user_input = input(f"\n{left_margin}{prompt}").strip()

        if user_input.isdigit():
            if valid_num_range is None:
                cli.error("No se aceptan valores numéricos.")
            else:
                min = valid_num_range[0]
                max = valid_num_range[1]
                num = int(user_input)

                if min <= num <= max:
                    return user_input
                else:
                    cli.error(f"Ingrese un valor entre {min} y {max}.")
        else:
            if admits_text:
                if user_input == "" and not admits_emty_string:
                    cli.error("El campo no puede estar vacío.")
                else:
                    return user_input
            else:
                cli.error("Ingrese un valor numérico.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por teclado")
        sys.exit(130)
