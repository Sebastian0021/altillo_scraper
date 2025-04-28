from rich.console import Console
import readchar

console = Console()
console.print("[bold green]Test de Rich: Si ves esto en verde, funciona.[/bold green]")
console.print("Presiona flecha arriba o abajo. Presiona Enter para salir.")

while True:
    key = readchar.readkey()
    if key == readchar.key.UP:
        console.print("Arriba", style="cyan")
    elif key == readchar.key.DOWN:
        console.print("Abajo", style="magenta")
    elif key == readchar.key.ENTER or key == "\r" or key == "\n":
        break
