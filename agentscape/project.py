from pathlib import Path


def find_nearest_python_file(start_dir: Path) -> Path | None:
    """Find the Python file closest to the given directory.

    Returns None if no Python file is found.
    """
    # Get all Python files
    python_files = list(start_dir.rglob("*.py"))

    if not python_files:
        return None

    # Sort by number of parts in path (fewer parts = higher in tree)
    return sorted(python_files, key=lambda p: len(p.parts))[0]


def is_project_root(path: Path) -> bool:
    """Check if the given path is a Python project root."""
    return any(
        (path / marker).exists()
        for marker in [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            "uv.lock",
        ]
    )


def find_project_root(start_dir: Path) -> Path | None:
    """Try to find project root by traversing up."""
    current = start_dir
    while current != current.parent:
        if is_project_root(current):
            return current

        current = current.parent

    return None


def get_project_root() -> Path:
    """Find the project root directory.

    Strategy:
    1. Try to find project root by traversing up
    2. Determine the nearest Python file
    3. Return current directory as last resort
    """
    current = Path.cwd()

    # First try to find project root by traversing up
    project_root = find_project_root(current)

    # Fall back to finding nearest Python file
    if nearest_py := find_nearest_python_file(project_root or current):
        return nearest_py.parent

    return project_root or current


def get_agents_dir():
    """Ensure the components directory exists in the project."""
    agents_dir = get_project_root() / "agents"
    agents_dir.mkdir(exist_ok=True)

    return agents_dir
