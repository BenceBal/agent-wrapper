import typer
from rich.console import Console
from .graph import app as graph

app = typer.Typer()
console = Console()

@app.command()
def ui():
    """
    Launch the Gradio Web UI for Drag-and-Drop Video Generation.
    """
    console.print("[bold green]Launching Video Studio...[/bold green]")
    from .ui import launch_ui
    launch_ui()

@app.command()
def generate(prompt: str):
    """
    Generate a video from a prompt using local Flux/LivePortrait.
    """
    console.print(f"[bold blue]Starting Video Agent...[/bold blue]")
    console.print(f"[cyan]Prompt:[/cyan] {prompt}")
    
    # Initialize State
    initial_state = {"prompt": prompt, "storyboard": [], "scenes": [], "current_scene": 0, "final_video": ""}
    
    # Run Graph
    try:
        final_state = graph.invoke(initial_state)
        console.print(f"[bold green]Video Generated![/bold green] Path: {final_state['final_video']}")
    except Exception as e:
        console.print(f"[bold red]Failed:[/bold red] {e}")

if __name__ == "__main__":
    app()
