import os
import sys
import requests
from altillo_scraper.pdf.pdf_utils import generar_pdf_seccion
from altillo_scraper.scraper.web import get_sections_years_links_from_file, save_scrap_analysis, download_links
from rich.console import Console
from rich.table import Table
from rich.style import Style
import readchar
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.console import Group
from rich.rule import Rule

BASE_URL = "https://www.altillo.com/examenes/"

console = Console()

def menu_dinamico_rich(opciones, titulo="Seleccione una opción:", separadores=None):
    '''
    Muestra un menú navegable con flechas y Rich. Devuelve el índice de la opción seleccionada.
    separadores: lista de índices donde se debe mostrar una línea visual (no seleccionable)
    '''
    if separadores is None:
        separadores = []
    seleccion = 0
    opciones_visibles = opciones.copy()
    # Mapear índice visual a índice real de opción
    def get_visual_map():
        visual_map = []
        real_idx = 0
        for i in range(len(opciones) + len(separadores)):
            if i in separadores:
                visual_map.append(None)  # None indica separador
            else:
                visual_map.append(real_idx)
                real_idx += 1
        return visual_map
    visual_map = get_visual_map()
    def render_menu():
        header = Align.center(f"[bold cyan]{titulo}")
        footer = Align.center("[magenta]Hecho por: [cyan]https://sebastianpenaloza.com[/cyan][/magenta]")
        menu_lines = []
        for i, visual_idx in enumerate(visual_map):
            if visual_idx is None:
                menu_lines.append(Rule(style="dim", characters="─"))
            else:
                opcion = opciones[visual_idx]
                # Centramos SOLO si es un año (4 dígitos)
                import re
                if re.fullmatch(r"\d{4}", opcion.strip()):
                    if i == seleccion:
                        menu_lines.append(Align.center(f"> [underline][bold green]{opcion}[/bold green][/underline]"))
                    else:
                        menu_lines.append(Align.center(f"  {opcion}"))
                else:
                    if i == seleccion:
                        menu_lines.append(f"> [underline][bold green]{opcion}[/bold green][/underline]")
                    else:
                        menu_lines.append(f"  {opcion}")
        menu = Align.center(Group(*menu_lines), vertical="middle")
        content = Group(
            header,
            "",
            menu,
            "",
            footer
        )
        panel = Panel(content, padding=(1,2), expand=True)
        return panel
    with Live(render_menu(), screen=True, refresh_per_second=20) as live:
        while True:
            key = readchar.readkey()
            # Saltar separadores al navegar
            if key == readchar.key.UP:
                while True:
                    seleccion = (seleccion - 1) % len(visual_map)
                    if visual_map[seleccion] is not None:
                        break
            elif key == readchar.key.DOWN:
                while True:
                    seleccion = (seleccion + 1) % len(visual_map)
                    if visual_map[seleccion] is not None:
                        break
            elif key == readchar.key.ENTER or key == "\r" or key == "\n":
                return visual_map[seleccion]
            elif key == readchar.key.CTRL_C:
                console.print("[red]Cancelado por el usuario.[/red]")
                sys.exit(0)
            live.update(render_menu())

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_url():
    while True:
        console.clear()
        console.rule("[bold cyan]Ingrese la ruta relativa de la página de exámenes")
        console.print("[white]Ingrese la parte de la URL de la página de los parciales de altillo.com luego de 'https://www.altillo.com/examenes/'[/white]", style="bold")
        console.print("")
        console.print("Ejemplo: uba/cbc/algebra/index.asp -> https://www.altillo.com/examenes/uba/cbc/algebra/index.asp", style="dim")
        
        rel_url = console.input("[bold yellow]Ruta[/bold yellow]: ").strip()
        if not rel_url:
            console.print("[red]La ruta no puede estar vacía. Intente nuevamente.[/red]")
            continue
        full_url = BASE_URL + rel_url
        return full_url, rel_url

def download_and_analyze(url):
    clear()
    resp = requests.get(url)
    resp.raise_for_status()
    html_content = resp.content.decode('latin1', errors='replace')
    estructura = get_sections_years_links_from_file(html_content=html_content, verbose=False)
    return estructura

def menu_secciones(estructura, materia):
    secciones = list(estructura.keys())
    opciones = secciones + ["Volver al menú principal"]
    materia_cap = materia.capitalize()
    while True:
        clear()
        header = f"[bold yellow]{materia_cap}[/bold yellow]"
        idx = menu_dinamico_rich(opciones, titulo=f"[center]{header}[/center]\nSeleccione la sección:")
        if idx == len(opciones) - 1:
            clear()
            return "menu_principal"
        else:
            clear()
            return secciones[idx]

def menu_anios(estructura, seccion, materia):
    anios = sorted(list(estructura[seccion].keys()))
    opciones = [f"{anio}" for anio in anios]
    separadores = []
    if opciones:
        separadores.append(len(opciones))
    opciones += ["Descargar TODOS los años", "Descargar un rango de años", "Descargar varios años", "Volver"]
    materia_cap = materia.capitalize()
    seccion_cap = seccion.capitalize()
    while True:
        clear()
        header = f"[bold yellow]{materia_cap} - {seccion_cap}[/bold yellow]"
        from rich.console import Console
        console = Console()
        console.print()  # Línea en blanco visual
        seleccion = menu_dinamico_rich(opciones, titulo=f"[center]{header}[/center]\nSeleccione el/los año/s a descargar:", separadores=separadores)
        if seleccion == len(opciones) - 1:  # Volver
            clear()
            return None
        elif seleccion == len(opciones) - 2:  # Descargar varios años
            entrada = console.input("[bold yellow]Ingrese años separados por coma (ej: 2020,2022,2023): [/bold yellow]").strip()
            seleccionados = [a for a in anios if a in [x.strip() for x in entrada.split(',')]]
            if seleccionados:
                return seleccionados
            console.print("[red]Años inválidos.[/red]")
            console.input("Presione Enter para continuar...")
            continue
        elif seleccion == len(opciones) - 3:  # Descargar un rango
            entrada = console.input("[bold yellow]Ingrese rango (ej: 2020-2023): [/bold yellow]").strip()
            try:
                ini, fin = entrada.split('-')
                ini, fin = int(ini), int(fin)
                seleccionados = [a for a in anios if ini <= int(a) <= fin]
                if seleccionados:
                    return seleccionados
            except Exception:
                pass
            console.print("[red]Rango inválido.[/red]")
            console.input("Presione Enter para continuar...")
            continue
        elif seleccion == len(opciones) - 4:  # Descargar TODOS los años
            return anios
        else:
            return [anios[seleccion]]

def menu_parciales(estructura, seccion, anio, materia, permitir_descarga_masiva=False):
    links = estructura[seccion][anio]
    opciones = [f"{i+1}. {' '.join(link_text.split())} - {link_href}" for i, (link_text, link_href) in enumerate(links)]
    separadores = []
    if opciones:
        separadores.append(len(opciones))
    if permitir_descarga_masiva:
        opciones += ["Descargar TODOS los parciales de TODOS los años SIN preguntar", "Descargar TODOS los parciales del año", "Volver"]
    else:
        opciones += ["Descargar TODOS los parciales del año", "Volver"]
    materia_cap = materia.capitalize()
    seccion_cap = seccion.capitalize()
    while True:
        clear()
        header = f"[bold yellow]{materia_cap} - {seccion_cap}[/bold yellow]"
        console = Console()
        console.print()  # Línea en blanco visual
        seleccion = menu_dinamico_rich(opciones, titulo=f"[center]{header}[/center]\nAño: {anio}\nSeleccione los parciales a descargar:", separadores=separadores)
        if permitir_descarga_masiva and seleccion == len(opciones) - 3:
            clear()
            return "descarga_masiva"
        if seleccion == len(opciones) - 1:  # Volver
            clear()
            return None
        elif (permitir_descarga_masiva and seleccion == len(opciones) - 2) or (not permitir_descarga_masiva and seleccion == len(opciones) - 2):
            clear()
            return links
        else:
            clear()
            return [links[seleccion]]

def navegar_carpetas_y_generar_pdf(base_dir='descargas', solo_enunciados=False):
    actual = base_dir
    while True:
        if not os.path.exists(actual):
            console.print(f"[red]No existe la carpeta {actual}[/red]")
            console.input("Presione Enter para volver...")
            return
        items = sorted(os.listdir(actual))
        dirs = [d for d in items if os.path.isdir(os.path.join(actual, d))]
        acciones = ["[bold green]Generar PDF de esta carpeta[/bold green]"]
        if os.path.abspath(actual) != os.path.abspath(base_dir):
            acciones.append("Carpeta anterior")
        acciones.append("Volver")
        opciones = [f"[bold blue]{d}/[/bold blue]" for d in dirs]
        if opciones:
            opciones.append("[dim]─────────────────────────────[/dim]")
        opciones += acciones
        seleccion = menu_dinamico_rich(
            opciones,
            titulo=f"[bold white]Carpeta actual:[/bold white] [bold cyan]{actual}[/bold cyan]\n[dim]Navegue con flechas y seleccione acción:[/dim]"
        )
        
        if seleccion < len(dirs):
            actual = os.path.join(actual, dirs[seleccion])
            continue
        if opciones[seleccion].startswith("[dim]"):
            continue
        accion_idx = seleccion - (len(dirs) + (1 if dirs else 0))
        if acciones[accion_idx].startswith("[bold green]"):
            generar_pdf_seccion(actual, solo_enunciados=solo_enunciados)
            console.input("\nPresione Enter para continuar...")
            clear()
            continue
        elif acciones[accion_idx].startswith("[yellow]"):
            actual = os.path.dirname(actual)
            continue
        elif acciones[accion_idx] == "Volver":
            return

def main():
    clear()
    opciones_menu = [
        "Descargar exámenes",
        "Descargar solo el enunciado (primera imagen) de cada parcial",
        "Generar PDF a partir de carpeta descargada",
        "Salir"
    ]
    while True:
        seleccion = menu_dinamico_rich(opciones_menu, titulo="Altillo Scraper CLI")
        
        # 1. Descargar exámenes (flujo cíclico)
        if seleccion == 0:
            while True:  # Menú URL
                url, rel_url = input_url()
                try:
                    estructura = download_and_analyze(url)
                except Exception as e:
                    error_msg = f"[red]Error al descargar o analizar la página:[/red]\n[red]{e}[/red]"
                    titulo_error = "[bold red]Algo salió mal[/bold red]\n" + error_msg
                    opciones_error = ["Volver al menú principal", "Volver a ingresar una nueva URL"]
                    eleccion = menu_dinamico_rich(opciones_error, titulo=titulo_error)
                    if eleccion == 0:
                        break  # Volver al principal
                    else:
                        continue  # Reintentar URL
                # Si la descarga fue exitosa, sigue flujo anidado
                # Extraer nombre de la materia desde rel_url
                partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                materia = partes[-1] if partes else "Materia"
                while True:  # Menú sección
                    seccion = menu_secciones(estructura, materia)
                    if seccion == "menu_principal":
                        break  # Volver al principal
                    while True:  # Menú año
                        anios = menu_anios(estructura, seccion, materia)
                        if anios is None:
                            break  # Volver a sección
                        while True:  # Menú parciales
                            # Si hay más de un año seleccionado, permitir descarga masiva
                            permitir_descarga_masiva = len(anios) > 1
                            parciales = menu_parciales(estructura, seccion, anios[0], materia, permitir_descarga_masiva=permitir_descarga_masiva)
                            if parciales is None:
                                break  # Volver a año
                            # Si el usuario eligió descarga masiva de TODOS los años
                            if permitir_descarga_masiva and parciales == "descarga_masiva":
                                todos_los_links = []
                                for anio in anios:
                                    todos_los_links.extend(estructura[seccion][anio])
                                partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                                materia = partes[-1] if partes else "materia"
                                for anio in anios:
                                    destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                                    links_anio = estructura[seccion][anio]
                                    console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                                    console.print(f"Descargando {len(links_anio)} archivos a {destino} ...", style="cyan")
                                    base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                                    download_links(links_anio, base_url, destino)
                                    console.input("\nDescarga finalizada. Presione Enter para continuar...")
                                    clear()
                                break
                            # Lógica de descarga normal
                            partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                            materia = partes[-1] if partes else "materia"
                            destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anios[0])
                            console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                            console.print(f"Descargando {len(parciales)} archivos a {destino} ...", style="cyan")
                            base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                            download_links(parciales, base_url, destino)
                            console.input("\nDescarga finalizada. Presione Enter para volver al menú de parciales...")
                            clear()
                            # Vuelve solo un nivel atrás (menú parciales)
                        # Si sale del menú de parciales, vuelve al menú de años
                    # Si sale del menú de años, vuelve al menú de secciones
                # Si sale del menú de secciones, vuelve al menú principal
                break
        # 2. Descargar solo el enunciado (similar, pero ajustado a ese flujo)
        elif seleccion == 1:
            while True:
                url, rel_url = input_url()
                try:
                    estructura = download_and_analyze(url)
                except Exception as e:
                    error_msg = f"[red]Error al descargar o analizar la página:[/red]\n[red]{e}[/red]"
                    titulo_error = "[bold red]Algo salió mal[/bold red]\n" + error_msg
                    opciones_error = ["Volver al menú principal", "Volver a ingresar una nueva URL"]
                    eleccion = menu_dinamico_rich(opciones_error, titulo=titulo_error)
                    if eleccion == 0:
                        break
                    else:
                        continue
                partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                materia = partes[-1] if partes else "Materia"
                while True:
                    seccion = menu_secciones(estructura, materia)
                    if seccion == "menu_principal":
                        break
                    while True:
                        anios = menu_anios(estructura, seccion, materia)
                        if anios is None:
                            break
                        while True:
                            parciales = menu_parciales(estructura, seccion, anios[0], materia)
                            if parciales is None:
                                break
                            # Lógica de descarga de solo enunciado
                            partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                            materia = partes[-1] if partes else "materia"
                            destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anios[0])
                            console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                            console.print(f"Descargando SOLO el enunciado (primera imagen) de {len(parciales)} parciales a {destino} ...", style="cyan")
                            base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                            download_links(parciales, base_url, destino, solo_primera_imagen=True)
                            console.input("\nDescarga de enunciado finalizada. Presione Enter para volver al menú de parciales...")
                            clear()
                        # Sale a menú de años
                    # Sale a menú de secciones
                break
        # 3. Generar PDF
        elif seleccion == 2:  # Generar PDF a partir de carpeta descargada
            while True:
                opciones_pdf = [
                    "Generar PDF completo (todas las imágenes y páginas)",
                    "Generar solo enunciados (primera imagen/página de cada parcial)",
                    "Volver al menú principal"
                ]
                eleccion_pdf = menu_dinamico_rich(opciones_pdf, titulo="¿Qué tipo de PDF quieres generar?")
                if eleccion_pdf == 2:
                    break  # Volver al menú principal
                solo_enunciados = (eleccion_pdf == 1)
                navegar_carpetas_y_generar_pdf(solo_enunciados=solo_enunciados)
                # Al finalizar, vuelve a este menú PDF
        # 4. Salir
        elif seleccion == 3:
            console.print("[bold cyan]¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
