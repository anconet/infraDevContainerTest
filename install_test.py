"""Black-box command-line tests for install.py."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

INSTALL_SCRIPT = Path(__file__).parent / "infraDevContainer" / "install.py"
SOURCE_FILE_NAMES = ("Dockerfile", "devcontainer.json", "post-create.sh")
PYTHON = sys.executable


def run(args, *, project_root=None, stdin=None, script=None):
    """Invoke install.py as a subprocess and return the CompletedProcess result."""
    script = script or INSTALL_SCRIPT
    cmd = [PYTHON, str(script)] + list(args)
    if project_root is not None:
        cmd += ["--project-root", str(project_root)]
    return subprocess.run(cmd, capture_output=True, text=True, input=stdin)


class TestInstallCopy:
    """Tests for install --method copy."""

    def test_creates_devcontainer_directory(self, tmp_path):
        result = run(["install", "--method", "copy"], project_root=tmp_path)
        assert result.returncode == 0
        assert (tmp_path / ".devcontainer").is_dir()

    def test_copies_all_three_files(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        for name in SOURCE_FILE_NAMES:
            assert (tmp_path / ".devcontainer" / name).exists()

    def test_copied_files_are_not_symlinks(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        for name in SOURCE_FILE_NAMES:
            assert not (tmp_path / ".devcontainer" / name).is_symlink()

    def test_prints_success_message(self, tmp_path):
        result = run(["install", "--method", "copy"], project_root=tmp_path)
        assert "Installed 3 files" in result.stdout
        assert "copy" in result.stdout

    def test_fails_if_devcontainer_already_exists(self, tmp_path):
        (tmp_path / ".devcontainer").mkdir()
        result = run(["install", "--method", "copy"], project_root=tmp_path)
        assert result.returncode != 0
        assert "already exists" in result.stderr


class TestInstallSymlink:
    """Tests for install --method symlink."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_creates_devcontainer_directory(self, tmp_path):
        result = run(["install", "--method", "symlink"], project_root=tmp_path)
        assert result.returncode == 0
        assert (tmp_path / ".devcontainer").is_dir()

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_creates_symlinks_for_all_three_files(self, tmp_path):
        run(["install", "--method", "symlink"], project_root=tmp_path)
        for name in SOURCE_FILE_NAMES:
            assert (tmp_path / ".devcontainer" / name).is_symlink()

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_symlinks_are_relative(self, tmp_path):
        run(["install", "--method", "symlink"], project_root=tmp_path)
        for name in SOURCE_FILE_NAMES:
            link = tmp_path / ".devcontainer" / name
            assert not Path(os.readlink(link)).is_absolute()

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_symlinks_resolve_to_correct_content(self, tmp_path):
        run(["install", "--method", "symlink"], project_root=tmp_path)
        script_dir = INSTALL_SCRIPT.parent
        for name in SOURCE_FILE_NAMES:
            link = tmp_path / ".devcontainer" / name
            assert link.read_text() == (script_dir / name).read_text()

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_softlink_alias_accepted(self, tmp_path):
        result = run(["install", "--method", "softlink"], project_root=tmp_path)
        assert result.returncode == 0
        for name in SOURCE_FILE_NAMES:
            assert (tmp_path / ".devcontainer" / name).is_symlink()

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_fails_if_devcontainer_already_exists(self, tmp_path):
        (tmp_path / ".devcontainer").mkdir()
        result = run(["install", "--method", "symlink"], project_root=tmp_path)
        assert result.returncode != 0
        assert "already exists" in result.stderr


class TestInstallDefault:
    """Tests for install default behavior (no --method specified)."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_default_method_is_symlink(self, tmp_path):
        run(["install"], project_root=tmp_path)
        for name in SOURCE_FILE_NAMES:
            assert (tmp_path / ".devcontainer" / name).is_symlink()


class TestUninstall:
    """Tests for the uninstall command."""

    def test_removes_files_and_directory_with_force(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        result = run(["uninstall", "--yes"], project_root=tmp_path)
        assert result.returncode == 0
        assert not (tmp_path / ".devcontainer").exists()

    def test_prints_success_message(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        result = run(["uninstall", "--yes"], project_root=tmp_path)
        assert "Removed 3 files" in result.stdout

    def test_requires_confirmation_without_yes_flag(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        run(["uninstall"], project_root=tmp_path, stdin="n\n")
        assert (tmp_path / ".devcontainer").exists()

    def test_accepts_y_as_confirmation(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        result = run(["uninstall"], project_root=tmp_path, stdin="y\n")
        assert result.returncode == 0
        assert not (tmp_path / ".devcontainer").exists()

    def test_accepts_yes_as_confirmation(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        result = run(["uninstall"], project_root=tmp_path, stdin="yes\n")
        assert result.returncode == 0
        assert not (tmp_path / ".devcontainer").exists()

    def test_prints_cancelled_when_declined(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        result = run(["uninstall"], project_root=tmp_path, stdin="n\n")
        assert "cancelled" in result.stdout.lower()

    def test_fails_if_no_devcontainer(self, tmp_path):
        result = run(["uninstall", "--yes"], project_root=tmp_path)
        assert result.returncode != 0
        assert "No .devcontainer directory" in result.stderr

    def test_fails_if_devcontainer_is_a_file(self, tmp_path):
        (tmp_path / ".devcontainer").touch()
        result = run(["uninstall", "--yes"], project_root=tmp_path)
        assert result.returncode != 0
        assert "Expected a directory" in result.stderr

    def test_fails_if_extra_files_in_devcontainer(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        (tmp_path / ".devcontainer" / "extra.txt").touch()
        result = run(["uninstall", "--yes"], project_root=tmp_path)
        assert result.returncode != 0
        assert "extra files" in result.stderr

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_removes_symlinks(self, tmp_path):
        run(["install", "--method", "symlink"], project_root=tmp_path)
        result = run(["uninstall", "--yes"], project_root=tmp_path)
        assert result.returncode == 0
        assert not (tmp_path / ".devcontainer").exists()


class TestArgumentErrors:
    """Tests for invalid or missing command-line arguments."""

    def test_no_operation_exits_nonzero(self):
        result = run([])
        assert result.returncode != 0

    def test_invalid_method_exits_nonzero(self, tmp_path):
        result = run(["install", "--method", "invalid"], project_root=tmp_path)
        assert result.returncode != 0

    def test_nonexistent_project_root_exits_nonzero(self, tmp_path):
        result = run(["install", "--method", "copy"], project_root=tmp_path / "nonexistent")
        assert result.returncode != 0

    def test_project_root_as_file_exits_nonzero(self, tmp_path):
        f = tmp_path / "file.txt"
        f.touch()
        result = run(["install", "--method", "copy"], project_root=f)
        assert result.returncode != 0


class TestMissingSourceFiles:
    """Tests for behavior when install.py is run without its source files."""

    def test_install_fails_and_leaves_no_devcontainer(self, tmp_path):
        # Create a temp dir with only install.py — no Dockerfile etc.
        script_dir = tmp_path / "infraDevContainer"
        script_dir.mkdir()
        shutil.copy(INSTALL_SCRIPT, script_dir / "install.py")
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = run(
            ["install", "--method", "copy"],
            project_root=project_root,
            script=script_dir / "install.py",
        )

        assert result.returncode != 0
        assert "Required source file is missing" in result.stderr
        assert not (project_root / ".devcontainer").exists()


class TestIntegration:
    """Full install/uninstall workflow tests."""

    def test_full_copy_workflow(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        assert (tmp_path / ".devcontainer").is_dir()
        for name in SOURCE_FILE_NAMES:
            assert (tmp_path / ".devcontainer" / name).exists()

        run(["uninstall", "--yes"], project_root=tmp_path)
        assert not (tmp_path / ".devcontainer").exists()

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks not reliable on Windows")
    def test_full_symlink_workflow(self, tmp_path):
        run(["install", "--method", "symlink"], project_root=tmp_path)
        assert (tmp_path / ".devcontainer").is_dir()
        for name in SOURCE_FILE_NAMES:
            assert (tmp_path / ".devcontainer" / name).is_symlink()

        run(["uninstall", "--yes"], project_root=tmp_path)
        assert not (tmp_path / ".devcontainer").exists()

    def test_reinstall_blocked_without_uninstall(self, tmp_path):
        run(["install", "--method", "copy"], project_root=tmp_path)
        result = run(["install", "--method", "copy"], project_root=tmp_path)
        assert result.returncode != 0
        assert "already exists" in result.stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
