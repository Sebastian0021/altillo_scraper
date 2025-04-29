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

BASE_URL = "https://www.altillo.com/examenes/"

console = Console()

def menu_dinamico_rich(opciones, titulo="Seleccione una opción:"):
    '''
    Muestra un menú navegable con flechas y Rich. Devuelve el índice de la opción seleccionada.
    Ahora usa Live(screen=True) para mejorar la experiencia en Windows CMD.
    '''
    seleccion = 0
    def render_menu():
        lines = [f"[bold cyan]{titulo}"]
        for i, opcion in enumerate(opciones):
            if i == seleccion:
                lines.append(f"> [underline][bold green]{opcion}[/bold green][/underline]")
            else:
                lines.append(f"  {opcion}")
        lines.append("[magenta]Hecho por: [cyan]https://sebastianpenaloza.com[/cyan][/magenta]")
        # Panel para centrar y evitar overflow
        return Panel(Align.center("\n".join(lines), vertical="middle"), padding=(1,2))

    with Live(render_menu(), screen=True, refresh_per_second=10, transient=False) as live:
        while True:
            key = readchar.readkey()
            if key == readchar.key.UP:
                seleccion = (seleccion - 1) % len(opciones)
            elif key == readchar.key.DOWN:
                seleccion = (seleccion + 1) % len(opciones)
            elif key == readchar.key.ENTER or key == "\r" or key == "\n":
                return seleccion
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
    print(f"Descargando página: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    html_content = resp.content.decode('latin1', errors='replace')
    print("Página descargada. Analizando...")
    estructura = get_sections_years_links_from_file(html_content=html_content, verbose=False)
    return estructura

def menu_secciones(estructura):
    secciones = list(estructura.keys())
    opciones = secciones + ["Volver al menú principal"]
    while True:
        clear()
        idx = menu_dinamico_rich(opciones, titulo="Seleccione la sección:")
        if idx == len(opciones) - 1:
            clear()
            return "menu_principal"
        else:
            clear()
            return secciones[idx]

def menu_anios(estructura, seccion):
    anios = sorted(list(estructura[seccion].keys()))
    opciones = [f"{anio}" for anio in anios] + ["Descargar TODOS los años", "Descargar un rango", "Descargar varios años", "Volver"]
    while True:
        clear()
        seleccion = menu_dinamico_rich(opciones, titulo=f"Sección: {seccion}\nSeleccione el/los año/s a descargar:")
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

def menu_parciales(estructura, seccion, anio, permitir_descarga_masiva=False):
    links = estructura[seccion][anio]
    opciones = [f"{i+1}. {' '.join(link_text.split())} - {link_href}" for i, (link_text, link_href) in enumerate(links)] + ["Descargar TODOS los parciales del año", "Volver"]
    if permitir_descarga_masiva:
        opciones.insert(-1, "Descargar TODOS los parciales de TODOS los años SIN preguntar")
    while True:
        clear()
        seleccion = menu_dinamico_rich(opciones, titulo=f"Sección: {seccion} | Año: {anio}\nSeleccione los parciales a descargar:")
        if permitir_descarga_masiva and seleccion == len(opciones) - 2:
            clear()
            return "descarga_masiva"
        if seleccion == len(opciones) - 1:  # Volver
            clear()
            return None
        elif seleccion == len(opciones) - (3 if permitir_descarga_masiva else 2):  # Descargar TODOS
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
            acciones.append("[yellow]Carpeta anterior[/yellow]")
        acciones.append("[red]Volver al menú principal[/red]")
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
        elif acciones[accion_idx].startswith("[red]"):
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
        
        if seleccion == 0:  # Descargar exámenes (todas las imágenes)
            url, rel_url = input_url()
            try:
                estructura = download_and_analyze(url)
            except Exception as e:
                console.print(f"[red]Error al descargar o analizar la página: {e}[/red]")
            seccion = menu_secciones(estructura)
            if seccion == "menu_principal":
                clear()
                continue
            anios = menu_anios(estructura, seccion)
            if not anios:
                continue
            # Si el usuario seleccionó TODOS los años, permite la descarga masiva desde el menú de parciales
            if hasattr(anios, '__iter__') and not isinstance(anios, str) and len(anios) > 1:
                descarga_masiva = False
                for anio in anios:
                    seleccionados = menu_parciales(estructura, seccion, anio, permitir_descarga_masiva=True)
                    if seleccionados == "descarga_masiva":
                        descarga_masiva = True
                        break
                    if not seleccionados:
                        continue
                    partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                    materia = partes[-1] if partes else "materia"
                    destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                    console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                    console.print(f"Descargando {len(seleccionados)} archivos a {destino} ...", style="cyan")
                    base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                    download_links(seleccionados, base_url, destino, solo_primera_imagen=True)
                    console.input(f"[green]\nDescarga finalizada para {anio}. Presione Enter para continuar...[/green]")
                    clear()
                if descarga_masiva:
                    # Descargar todos los enunciados (primera imagen) de todos los años sin preguntar más
                    for anio in anios:
                        links_todos = estructura[seccion][anio]
                        if not links_todos:
                            continue
                        partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                        materia = partes[-1] if partes else "materia"
                        destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                        console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                        console.print(f"Descargando SOLO el enunciado (primera imagen) de TODOS los parciales ({len(links_todos)}) de {anio} a {destino} ...", style="cyan")
                        base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                        download_links(links_todos, base_url, destino, solo_primera_imagen=True)
                        console.input(f"[green]\nDescarga finalizada para {anio}. Presione Enter para continuar...[/green]")
                        clear()
            else:
                for anio in anios:
                    seleccionados = menu_parciales(estructura, seccion, anio)
                    if not seleccionados:
                        continue
                    partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                    materia = partes[-1] if partes else "materia"
                    destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                    console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                    console.print(f"Descargando {len(seleccionados)} archivos a {destino} ...", style="cyan")
                    base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                    download_links(seleccionados, base_url, destino)
                    console.input(f"[green]\nDescarga finalizada para {anio}. Presione Enter para continuar...[/green]")
                    clear()
        elif seleccion == 1:  # Descargar solo primera imagen (posible enunciado)
            url, rel_url = input_url()
            try:
                estructura = download_and_analyze(url)
            except Exception as e:
                console.print(f"[red]Error al descargar o analizar la página: {e}[/red]")
            seccion = menu_secciones(estructura)
            if seccion == "menu_principal":
                continue
            anios = menu_anios(estructura, seccion)
            if not anios:
                continue
            # Permitir descarga masiva de enunciados si el usuario seleccionó TODOS los años
            if hasattr(anios, '__iter__') and not isinstance(anios, str) and len(anios) > 1:
                descarga_masiva = False
                for anio in anios:
                    seleccionados = menu_parciales(estructura, seccion, anio, permitir_descarga_masiva=True)
                    if seleccionados == "descarga_masiva":
                        descarga_masiva = True
                        break
                    if not seleccionados:
                        continue
                    partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                    materia = partes[-1] if partes else "materia"
                    destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                    console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                    console.print(f"Descargando SOLO el enunciado (primera imagen) de {len(seleccionados)} parciales a {destino} ...", style="cyan")
                    base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                    download_links(seleccionados, base_url, destino, solo_primera_imagen=True)
                    console.input(f"[green]\nDescarga finalizada para {anio}. Presione Enter para continuar...[/green]")
                    clear()
                if descarga_masiva:
                    # Descargar todos los enunciados (primera imagen) de todos los años sin preguntar más
                    for anio in anios:
                        links_todos = estructura[seccion][anio]
                        if not links_todos:
                            continue
                        partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                        materia = partes[-1] if partes else "materia"
                        destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                        console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                        console.print(f"Descargando SOLO el enunciado (primera imagen) de TODOS los parciales ({len(links_todos)}) de {anio} a {destino} ...", style="cyan")
                        base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                        download_links(links_todos, base_url, destino, solo_primera_imagen=True)
                        console.input(f"[green]\nDescarga finalizada para {anio}. Presione Enter para continuar...[/green]")
                        clear()
            else:
                for anio in anios:
                    seleccionados = menu_parciales(estructura, seccion, anio)
                    if not seleccionados:
                        continue
                    partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                    materia = partes[-1] if partes else "materia"
                    destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                    console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                    console.print(f"Descargando SOLO el enunciado (primera imagen) de {len(seleccionados)} parciales a {destino} ...", style="cyan")
                    base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                    download_links(seleccionados, base_url, destino, solo_primera_imagen=True)
                    console.input(f"[green]\nDescarga finalizada para {anio}. Presione Enter para continuar...[/green]")
                    clear()
        elif seleccion == 2:  # Generar PDF a partir de carpeta descargada
            # Preguntar si quiere solo enunciados o PDF completo
            opciones_pdf = [
                "Generar PDF completo (todas las imágenes y páginas)",
                "Generar solo enunciados (primera imagen/página de cada parcial)",
                "Volver al menú principal"
            ]
            eleccion_pdf = menu_dinamico_rich(opciones_pdf, titulo="¿Qué tipo de PDF quieres generar?")
            if eleccion_pdf == 2:
                continue
            solo_enunciados = (eleccion_pdf == 1)
            navegar_carpetas_y_generar_pdf(solo_enunciados=solo_enunciados)
        elif seleccion == 3:  # Salir
            console.print("¡Hasta luego!", style="bold green")
            break

if __name__ == "__main__":
    main()
