from pathlib import Path
from typing import Optional

import questionary
import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from agentscape import AGENTS_DIR
from agentscape.project import get_agents_dir, get_project_root

app = typer.Typer(
    name="agentkit",
    help="A modern CLI tool for installing AI agent components",
    add_completion=False,
)

console = Console()


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
        for path in AGENTS_DIR.glob("*.py")
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
            ctx.invoke(add_agent, agent=agent, destination=None)
        else:
            raise typer.Exit()


@app.command("add")
def add_agent(
    agent: str = typer.Argument(..., help="Name of the agent to add"),
    destination: Optional[str] = typer.Option(
        None, "--dest", "-d", help="Custom destination directory"
    ),
):
    """Add an AI agent component to your project."""
    try:
        target_dir = get_agents_dir() if not destination else Path(destination)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{agent}.py"

        if target_path.exists():
            overwrite = questionary.confirm(
                f"Agent {agent} already exists. Overwrite?", default=False
            ).ask()

            if not overwrite:
                rprint("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit()

        source_path = AGENTS_DIR / f"{agent}.py"
        target_path.write_text(source_path.read_text())

        relative_target_path = target_path.relative_to(Path.cwd())

        rprint(f"[green]✓[/green] Added {agent} agent to {relative_target_path}")
        rprint(Panel(example_usage(target_path, agent), title="Example usage"))

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("list")
def list_agents():
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
