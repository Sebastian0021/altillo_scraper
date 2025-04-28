import os
import sys
import requests
from main import get_sections_years_links_from_file, save_scrap_analysis, download_links
from rich.console import Console
from rich.table import Table
from rich.style import Style
import readchar

BASE_URL = "https://www.altillo.com/examenes/"

console = Console()

def menu_dinamico_rich(opciones, titulo="Seleccione una opción:"):
    '''
    Muestra un menú navegable con flechas y Rich. Devuelve el índice de la opción seleccionada.
    '''
    seleccion = 0
    while True:
        console.clear()
        console.rule(f"[bold cyan]{titulo}")
        for i, opcion in enumerate(opciones):
            if i == seleccion:
                console.print(f"> [underline][bold green]{opcion}[/bold green][/underline]")
            else:
                console.print(f"  {opcion}")
        # Barra decorativa SIEMPRE visible abajo
        console.rule("[magenta]Hecho por: [cyan]https://sebastianpenaloza.com[/cyan][/magenta]")
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

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_url():
    while True:
        console.clear()
        console.rule("[bold cyan]Ingrese la ruta relativa de la página de exámenes")
        console.print("[white]Ingrese la parte de la URL de la página de los parciales de altillo.com luego de 'https://www.altillo.com/examenes/'[/white]", style="bold")
        console.print("")
        console.print("Ejemplo: uba/cbc/algebra/index.asp -> https://www.altillo.com/examenes/uba/cbc/algebra/index.asp", style="dim")
        console.rule("[magenta]Hecho por: [cyan]https://sebastianpenaloza.com[/cyan][/magenta]")
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
    estructura = get_sections_years_links_from_file(html_content=html_content)
    return estructura

def menu_secciones(estructura):
    secciones = list(estructura.keys())
    opciones = secciones + ["Volver al menú principal"]
    while True:
        idx = menu_dinamico_rich(opciones, titulo="Seleccione la sección:")
        if idx == len(opciones) - 1:
            return "menu_principal"
        else:
            return secciones[idx]

def menu_anios(estructura, seccion):
    anios = sorted(list(estructura[seccion].keys()))
    opciones = [f"{anio}" for anio in anios] + ["Descargar TODOS los años", "Descargar un rango", "Descargar varios años", "Volver"]
    while True:
        seleccion = menu_dinamico_rich(opciones, titulo=f"Sección: {seccion}\nSeleccione el/los año/s a descargar:")
        if seleccion == len(opciones) - 1:  # Volver
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

def menu_parciales(estructura, seccion, anio):
    links = estructura[seccion][anio]
    opciones = [f"{i+1}. {' '.join(link_text.split())} - {link_href}" for i, (link_text, link_href) in enumerate(links)] + ["Descargar TODOS los parciales del año", "Volver"]
    while True:
        seleccion = menu_dinamico_rich(opciones, titulo=f"Sección: {seccion} | Año: {anio}\nSeleccione los parciales a descargar:")
        if seleccion == len(opciones) - 1:  # Volver
            return None
        elif seleccion == len(opciones) - 2:  # Descargar TODOS
            return links
        else:
            return [links[seleccion]]

from pdf_utils import generar_pdf_seccion

def navegar_carpetas_y_generar_pdf(base_dir='descargas'):
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
        # Barra inferior de autoría
        console.rule("[magenta]Hecho por: [cyan]https://sebastianpenaloza.com[/cyan][/magenta]")
        # Si selecciona una carpeta, navega
        if seleccion < len(dirs):
            actual = os.path.join(actual, dirs[seleccion])
            continue
        # Si selecciona la línea separadora, no hace nada
        if opciones[seleccion].startswith("[dim]"):
            continue
        # Acciones
        accion_idx = seleccion - (len(dirs) + (1 if dirs else 0))
        if acciones[accion_idx].startswith("[bold green]"):
            generar_pdf_seccion(actual)
            console.input("\nPresione Enter para continuar...")
            continue
        elif acciones[accion_idx].startswith("[yellow]"):
            actual = os.path.dirname(actual)
            continue
        elif acciones[accion_idx].startswith("[red]"):
            return


def main():
    opciones_menu = ["Descargar exámenes", "Generar PDF a partir de carpeta descargada", "Salir"]
    while True:
        seleccion = menu_dinamico_rich(opciones_menu, titulo="Altillo Scraper CLI")
        console.rule("[magenta]Hecho por: [cyan]https://sebastianpenaloza.com[/cyan][/magenta]")
        if seleccion == 0:  # Descargar exámenes
            url, rel_url = input_url()
            try:
                estructura = download_and_analyze(url)
            except Exception as e:
                console.print(f"[red]Error al descargar o analizar la página: {e}[/red]")
                console.input("[bold yellow]Presione Enter para volver al menú principal...[/bold yellow]")
                continue
            while True:
                seccion = menu_secciones(estructura)
                if seccion == "menu_principal":
                    break  # Volver al menú principal
                anios = menu_anios(estructura, seccion)
                if anios is None:
                    continue  # Volver a seleccionar sección
                # Soportar lista de años
                for anio in anios:
                    seleccionados = menu_parciales(estructura, seccion, anio)
                    if seleccionados is None:
                        continue  # Saltar a otro año o volver a seleccionar sección
                    partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                    materia = partes[-1] if partes else "materia"
                    destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                    console.print(f"[bold yellow]Carpeta destino:[/bold yellow] [dim]{destino}[/dim]")
                    console.print(f"Descargando {len(seleccionados)} archivos a {destino} ...", style="cyan")
                    base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                    download_links(seleccionados, base_url, destino)
                    console.input(f"[green]\nDescarga finalizada para {anio}. Presione Enter para continuar...[/green]")
                # Al finalizar todos los años, vuelve a menú de secciones para seguir descargando

        elif seleccion == 1:  # Generar PDF
            navegar_carpetas_y_generar_pdf()
        elif seleccion == 2:  # Salir
            console.print("¡Hasta luego!", style="bold green")
            break


if __name__ == "__main__":
    main()
