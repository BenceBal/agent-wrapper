import typer
from rich.console import Console
from .orchestrator import Orchestrator

app = typer.Typer()
console = Console()

@app.command()
def build(task: str):
    """
    Start the Agentic Build Loop for a given task.
    """
    console.print(f"[bold green]Starting Agent Wrapper...[/bold green]")
    console.print(f"[cyan]Task:[/cyan] {task}")
    
    # Initialize the Brain
    brain = Orchestrator()
    
    # Execute Plan
    try:
        result = brain.execute(task)
        console.print(f"[bold green]Success![/bold green] Output:\n{result}")
    except Exception as e:
        console.print(f"[bold red]Failed:[/bold red] {e}")

@app.command()
def interactive():
    """
    Launch interactive TUI mode.
    """
    console.print("[yellow]Interactive Mode (Coming Soon)[/yellow]")

if __name__ == "__main__":
    app()
