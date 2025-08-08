import os
from time import sleep

left_margin = " " * 4
min_box_width = 50

double_top_left = "╔"
double_top_right = "╗"
double_bottom_left = "╚"
double_bottom_right = "╝"
double_horizontal = "═"
double_vertical = "║"

top_left = "┌"
top_right = "┐"
bottom_left = "└"
bottom_right = "┘"
horizontal = "─"
vertical = "│"
left_t = "├"
right_t = "┤"


def draw_heading(text: str, width=min_box_width):
    box_width = max(len(text) + 6, width)

    print(
        f"\n{left_margin}{double_top_left}{double_horizontal * (box_width - 2)}{double_top_right}"
    )
    print(f"{left_margin}{double_vertical}{' ' * (box_width - 2)}{double_vertical}")

    print(
        f"{left_margin}{double_vertical}  {text.center(box_width - 6)}  {double_vertical}"
    )
    print(f"{left_margin}{double_vertical}{' ' * (box_width - 2)}{double_vertical}")

    print(
        f"{left_margin}{double_bottom_left}{double_horizontal * (box_width - 2)}{double_bottom_right}"
    )


def draw_primary_box(heading: str, content: list[str], width: int = min_box_width):
    # Calcular el ancho necesario para el título
    # 2 por los espacios en blanco y 2 por los bordes ||
    heading_width = len(heading) + 4

    # Obtenemos la línea más larga del contenido dentro de la caja
    content_width = max([len(i) + 4 for i in content]) if content else 0

    # El ancho final de la caja es el mayor entre el ancho del título,
    # el del contenido y el parámetro 'width', que es opcional
    box_width = max(heading_width, content_width, width)

    # Imprimir la caja línea por línea
    print(f"\n{left_margin}{top_left}{horizontal * (box_width - 2)}{top_right}")
    print(f"{left_margin}{vertical}{heading.center(box_width - 2)}{vertical}")
    print(f"{left_margin}{left_t}{horizontal * (box_width - 2)}{right_t}")
    print(f"{left_margin}{vertical}{' ' * (box_width - 2)}{vertical}")

    if not content:
        print(
            f"{left_margin}{vertical}{' (Ningún dato añadido) '.ljust(box_width - 2)}{vertical}"
        )
    else:
        for line in content:
            line = truncate_text(line, box_width - 4)
            print(f"{left_margin}{vertical} {line.ljust(box_width - 4)} {vertical}")

    print(f"{left_margin}{vertical}{' ' * (box_width - 2)}{vertical}")
    print(f"{left_margin}{bottom_left}{horizontal * (box_width - 2)}{bottom_right}")


def draw_secondary_box(
    content: list[str],
    heading: str,
    width: int = min_box_width,
    subheading: str | None = None,
):
    # Calculamos el largo del título y subtitulo: longitud del
    # texto mas 2 de los espacios " " y 2 de los bordes ||
    heading_width = len(heading) + 4
    subheading_width = len(subheading) + 4 if subheading else 0

    # Obtenemos la línea más larga del contenido dentro de la caja
    content_width = max([len(i) + 4 for i in content]) if content else 0

    # El ancho de la caja es el mayor entre la longitud del titulo
    # subittulo, el largo del contenido o un mínimo prestablecido
    box_width = max(heading_width, subheading_width, content_width, width)

    # Mostramos la caja por pantalla, línea por línea
    print(
        f"\n{left_margin}{top_left}{horizontal}[ {heading} ]{horizontal * (box_width - len(heading) - 7)}{top_right}"
    )

    if subheading:
        print(f"{left_margin}{vertical}{' ' * (box_width - 2)}{vertical}")
        print(
            f"{left_margin}{vertical}{'  ' + subheading.ljust(box_width - 4)}{vertical}"
        )
        print(f"{left_margin}{left_t}{horizontal * (box_width - 2)}{right_t}")

    print(f"{left_margin}{vertical}{' ' * (box_width - 2)}{vertical}")

    if not content:
        print(
            f"{left_margin}{vertical}{' (Ningún dato añadido) '.ljust(box_width - 2)}{vertical}"
        )
    else:
        for line in content:
            line = truncate_text(line, box_width - 4)
            print(f"{left_margin}{vertical} {line.ljust(box_width - 4)} {vertical}")

    print(f"{left_margin}{vertical}{' ' * (box_width - 2)}{vertical}")
    print(f"{left_margin}{bottom_left}{horizontal * (box_width - 2)}{bottom_right}")


def truncate_text(text: str, max_width: int) -> str:
    """
    Función de conveniencia para truncar un texto en caso de superar
    el ancho establecido y añade una elipsis '..' al final de él
    """
    if len(text) > max_width:
        return f"{text[: max_width - 2]}.."
    else:
        return text


def error(text: str):
    print(f"{left_margin}ERROR: {text}")
    sleep(1.5)


def info(text: str):
    print(f"{left_margin}INFO: {text}")


def clear():
    os.system("cls" if os.name == "nt" else "clear")
