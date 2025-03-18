from pathlib import Path

from agentscape.project import get_agents_dir, get_project_root, get_tools_dir


def test_get_project_root_with_project_markers(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").touch()
    project_root = tmp_path / "my_project"
    project_root.mkdir()
    (project_root / "code.py").touch()

    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)
    assert get_project_root() == project_root


def test_get_project_root_in_nested_dir(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").touch()
    project_root = tmp_path / "my_project"
    project_root.mkdir()
    (project_root / "code.py").touch()

    nested_dir = project_root / "nested" / "dir"
    nested_dir.mkdir(parents=True)

    monkeypatch.setattr(Path, "cwd", lambda: nested_dir)
    assert get_project_root() == project_root


def test_get_project_root_with_nested_python_file(tmp_path, monkeypatch):
    nested_dir = tmp_path / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)
    test_file = nested_dir / "test.py"
    test_file.touch()

    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

    assert get_project_root() == nested_dir


def test_get_project_root_no_python_file(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)
    assert get_project_root() == tmp_path


def test_get_agents_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

    # Before calling get_agents_dir, directory should not exist
    agents_dir = tmp_path / "agents"
    assert not agents_dir.exists()

    # Get agents directory and verify it was created
    result = get_agents_dir()
    assert result == agents_dir
    assert agents_dir.exists()


def test_get_tools_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)

    # Before calling get_tools_dir, neither directory should exist
    agents_dir = tmp_path / "agents"
    tools_dir = agents_dir / "tools"
    assert not agents_dir.exists()
    assert not tools_dir.exists()

    # Get tools directory and verify it was created
    result = get_tools_dir()
    assert result == tools_dir
    assert tools_dir.exists()
    assert agents_dir.exists()
