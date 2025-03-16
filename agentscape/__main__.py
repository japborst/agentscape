from pathlib import Path
from typing import Optional

import questionary
import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="agentkit",
    help="A modern CLI tool for installing AI agent components",
    add_completion=False,
)

console = Console()

TEMPLATES_DIR = Path(__file__).parent / "agents"


def get_project_root() -> Path:
    """Find the project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise typer.BadParameter("Could not find project root (pyproject.toml)")


def ensure_agents_dir():
    """Ensure the components directory exists in the project."""
    project_root = get_project_root()
    agents_dir = project_root / "agents"
    agents_dir.mkdir(exist_ok=True)

    return agents_dir


def example_usage(target_path: Path, agent: str):
    """Return an example of how to use the installed agent."""
    project_root = get_project_root()
    import_path = str(target_path.relative_to(project_root).with_suffix("")).replace(
        "/", "."
    )
    return f"""[dim]from {import_path} import {agent}

# Run the agent
result = Runner.run({agent}, "Your prompt here")
print(result.final_output)[/dim]"""


def get_available_agents():
    """Get a list of available agent names."""
    return [
        path.stem
        for path in TEMPLATES_DIR.glob("*.py")
        if path.is_file() and not path.stem.startswith("_")
    ]


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Main command that shows available agents when no command is specified."""
    if ctx.invoked_subcommand is None:
        available_agents = get_available_agents()

        if not available_agents:
            rprint("[yellow]No available agents available[/yellow]")
            raise typer.Exit()

        agent = questionary.select(
            "Which agent would you like to install?", choices=available_agents
        ).ask()

        if agent:
            ctx.invoke(add, agent=agent, destination=None)
        else:
            raise typer.Exit()


@app.command()
def add(
    agent: str = typer.Argument(..., help="Name of the agent to add"),
    destination: Optional[str] = typer.Option(
        None, "--dest", "-d", help="Custom destination directory"
    ),
):
    """Add an AI agent component to your project."""
    try:
        target_dir = ensure_agents_dir() if not destination else Path(destination)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{agent}.py"

        if target_path.exists():
            overwrite = questionary.confirm(
                f"Agent {agent} already exists. Overwrite?", default=False
            ).ask()

            if not overwrite:
                rprint("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit()

        source_path = TEMPLATES_DIR / f"{agent}.py"
        target_path.write_text(source_path.read_text())

        rprint(f"[green]✓[/green] Added {agent} agent to {target_path}")
        rprint(Panel(example_usage(target_path, agent), title="Example usage"))

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def list():
    """List all available agents."""
    try:
        available_agents = get_available_agents()

        if not available_agents:
            rprint("[yellow]No available agents[/yellow]")
            raise typer.Exit()

        rprint(
            Panel(
                "\n".join(f"[blue]•[/blue] {agent}" for agent in available_agents),
                title="Available Agents",
                border_style="blue",
            )
        )

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
