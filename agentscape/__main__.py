from pathlib import Path
from typing import Optional

import questionary
import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from agentscape import AGENTS_DIR, TOOLS_DIR
from agentscape.models import ComponentType
from agentscape.project import get_component_dir, get_project_root

app = typer.Typer(
    name="agentscape",
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


def get_available_components(component_type: ComponentType) -> list[str]:
    """Get a list of available component names."""
    directory = AGENTS_DIR if component_type == ComponentType.AGENTS else TOOLS_DIR
    return sorted(
        [
            path.stem
            for path in directory.glob("*.py")
            if path.is_file() and not path.stem.startswith("_")
        ]
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Main command that shows available components when no command is specified."""
    if ctx.invoked_subcommand is None:
        component_type = questionary.select(
            "What would you like to install?",
            choices=[c.value for c in ComponentType],
        ).ask()

        if not component_type:
            raise typer.Exit()

        component_type_enum = ComponentType(component_type)
        available_items = get_available_components(component_type_enum)

        if not available_items:
            rprint(f"[yellow]No available {component_type}[/yellow]")
            raise typer.Exit()

        component = questionary.select(
            f"Which {component_type[:-1]} would you like to install?",
            choices=available_items,
        ).ask()

        if component:
            ctx.invoke(
                add_component,
                name=component,
                component_type=ComponentType(component_type),
                destination=None,
            )
        else:
            raise typer.Exit()


@app.command("add")
def add_component(
    component_type: ComponentType = typer.Argument(
        ComponentType.AGENTS,
        help="Type of component to add",
        case_sensitive=False,
    ),
    name: str = typer.Argument(..., help="Name of the component to add"),
    destination: Optional[str] = typer.Option(
        None, "--dest", "-d", help="Custom destination directory"
    ),
):
    """Add an AI agent or tool to your project."""
    try:
        target_dir = (
            get_component_dir(component_type) if not destination else Path(destination)
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{name}.py"

        if target_path.exists():
            overwrite = questionary.confirm(
                f"{component_type.value[:-1].title()} {name} already exists. Overwrite?",
                default=False,
            ).ask()

            if not overwrite:
                rprint("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit()

        source_dir = AGENTS_DIR if component_type == ComponentType.AGENTS else TOOLS_DIR
        source_path = source_dir / f"{name}.py"
        target_path.write_text(source_path.read_text())

        relative_target_path = target_path.relative_to(Path.cwd())
        component_name = component_type.value[:-1]

        rprint(
            f"[green]✓[/green] Added {component_name} {name} to {relative_target_path}"
        )
        if component_type == ComponentType.AGENTS:
            rprint(Panel(example_usage(target_path, name), title="Example usage"))

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command("list")
def list_components(
    component_type: ComponentType = typer.Argument(
        ComponentType.AGENTS,
        case_sensitive=False,
    ),
):
    """List all available agents or tools."""
    try:
        available_items = get_available_components(component_type)

        if not available_items:
            rprint(f"[yellow]No available {component_type.value}[/yellow]")
            raise typer.Exit()

        rprint(
            Panel(
                "\n".join(f"[blue]•[/blue] {item}" for item in available_items),
                title=f"Available {component_type.value.title()}",
                border_style="blue",
            )
        )

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
