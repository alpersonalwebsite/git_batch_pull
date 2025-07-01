"""
Comprehensive tests for GitService in the new architecture.
Tests clone, pull, clone_or_pull functionality and protocol switching.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from git_batch_pull.exceptions import GitOperationError
from git_batch_pull.models.repository import Repository, RepositoryInfo
from git_batch_pull.security import PathValidator, SafeSubprocessRunner
from git_batch_pull.services.git_service import GitService


@pytest.fixture
def temp_base_folder():
    """Create a temporary directory for test repositories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_subprocess_runner():
    """Mock SafeSubprocessRunner for testing."""
    return MagicMock(spec=SafeSubprocessRunner)


@pytest.fixture
def path_validator():
    """Real PathValidator for testing."""
    return PathValidator()


@pytest.fixture
def git_service(temp_base_folder, mock_subprocess_runner, path_validator):
    """GitService instance for testing."""
    return GitService(temp_base_folder, mock_subprocess_runner, path_validator)


@pytest.fixture
def sample_repository_info():
    """Sample repository info for testing."""
    return RepositoryInfo(
        name="test-repo",
        clone_url="https://github.com/user/test-repo.git",
        ssh_url="git@github.com:user/test-repo.git",
        default_branch="main",
        private=False,
        fork=False,
        archived=False,
    )


@pytest.fixture
def sample_repository(temp_base_folder, sample_repository_info):
    """Sample repository for testing."""
    return Repository(info=sample_repository_info, local_path=temp_base_folder / "test-repo")


class TestGitService:
    """Test cases for GitService functionality."""

    def test_get_repository_path(self, git_service):
        """Test repository path generation."""
        repo_path = git_service.get_repository_path("test-repo")
        assert repo_path.name == "test-repo"
        assert repo_path.parent == git_service.base_folder

    def test_get_repository_path_invalid_name(self, git_service):
        """Test repository path with invalid characters."""
        with pytest.raises(Exception):  # PathValidationError
            git_service.get_repository_path("../dangerous-repo")

    def test_has_uncommitted_changes_clean(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test has_uncommitted_changes with clean repository."""
        # Mock git status to return clean
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.has_uncommitted_changes(sample_repository.local_path)
        assert result is False

    def test_has_uncommitted_changes_dirty(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test has_uncommitted_changes with dirty repository."""
        # Mock git status to return changes
        mock_result = MagicMock()
        mock_result.stdout = "M  file.txt\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.has_uncommitted_changes(sample_repository.local_path)
        assert result is True

    def test_is_repository_empty_not_empty(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test is_repository_empty with commits."""
        # Mock git rev-parse to succeed (has commits)
        mock_result = MagicMock()
        mock_result.stdout = "abc123\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.is_repository_empty(sample_repository.local_path)
        assert result is False

    def test_is_repository_empty_empty(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test is_repository_empty with no commits."""
        # Mock git rev-parse to fail (no commits)
        mock_subprocess_runner.run_git_command.side_effect = GitOperationError("No HEAD")

        result = git_service.is_repository_empty(sample_repository.local_path)
        assert result is True

    def test_get_current_branch(self, git_service, sample_repository, mock_subprocess_runner):
        """Test getting current branch."""
        mock_result = MagicMock()
        mock_result.stdout = "main\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.get_current_branch(sample_repository.local_path)
        assert result == "main"

    def test_get_remote_url_https(self, git_service, sample_repository, mock_subprocess_runner):
        """Test getting HTTPS remote URL."""
        mock_result = MagicMock()
        mock_result.stdout = "https://github.com/user/test-repo.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.get_remote_url(sample_repository.local_path)
        assert result == "https://github.com/user/test-repo.git"

    def test_get_remote_url_ssh(self, git_service, sample_repository, mock_subprocess_runner):
        """Test getting SSH remote URL."""
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/test-repo.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.get_remote_url(sample_repository.local_path)
        assert result == "git@github.com:user/test-repo.git"

    def test_detect_protocol_ssh(self, git_service, sample_repository, mock_subprocess_runner):
        """Test protocol detection for SSH."""
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/test-repo.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.detect_protocol(sample_repository.local_path)
        assert result == "ssh"

    def test_detect_protocol_https(self, git_service, sample_repository, mock_subprocess_runner):
        """Test protocol detection for HTTPS."""
        mock_result = MagicMock()
        mock_result.stdout = "https://github.com/user/test-repo.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.detect_protocol(sample_repository.local_path)
        assert result == "https"

    def test_clone_repository_https(self, git_service, sample_repository, mock_subprocess_runner):
        """Test cloning repository with HTTPS."""
        git_service.clone_repository(sample_repository, use_ssh=False)

        # Verify git clone was called with HTTPS URL
        mock_subprocess_runner.run_git_command.assert_called_once_with(
            [
                "git",
                "clone",
                "https://github.com/user/test-repo.git",
                str(sample_repository.local_path),
            ],
            cwd=sample_repository.local_path.parent,
            timeout=300,
        )

    def test_clone_repository_ssh(self, git_service, sample_repository, mock_subprocess_runner):
        """Test cloning repository with SSH."""
        git_service.clone_repository(sample_repository, use_ssh=True)

        # Verify git clone was called with SSH URL
        mock_subprocess_runner.run_git_command.assert_called_once_with(
            [
                "git",
                "clone",
                "git@github.com:user/test-repo.git",
                str(sample_repository.local_path),
            ],
            cwd=sample_repository.local_path.parent,
            timeout=300,
        )

    def test_clone_repository_failure(self, git_service, sample_repository, mock_subprocess_runner):
        """Test clone repository failure handling."""
        mock_subprocess_runner.run_git_command.side_effect = GitOperationError("Clone failed")

        with pytest.raises(GitOperationError):
            git_service.clone_repository(sample_repository, use_ssh=False)

    def test_pull_repository_success(self, git_service, sample_repository, mock_subprocess_runner):
        """Test successful pull operation."""
        # Mock repository exists
        sample_repository.local_path.mkdir(parents=True)

        # Mock repository is not empty and has no uncommitted changes
        mock_result = MagicMock()
        mock_result.stdout = "abc123\n"
        mock_subprocess_runner.run_git_command.side_effect = [
            mock_result,  # git rev-parse (not empty)
            MagicMock(stdout=""),  # git status (clean)
            MagicMock(),  # git checkout
            MagicMock(),  # git pull
        ]

        git_service.pull_repository(sample_repository)

        # Verify checkout and pull were called
        calls = mock_subprocess_runner.run_git_command.call_args_list
        assert len(calls) == 4
        # Check checkout call
        assert calls[2][0][0] == ["git", "checkout", "main"]
        # Check pull call
        assert calls[3][0][0] == ["git", "pull", "origin", "main"]

    def test_pull_repository_uncommitted_changes(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test pull skipped when uncommitted changes exist."""
        # Mock repository exists
        sample_repository.local_path.mkdir(parents=True)

        # Mock repository has uncommitted changes
        mock_result_empty = MagicMock()
        mock_result_empty.stdout = "abc123\n"
        mock_result_dirty = MagicMock()
        mock_result_dirty.stdout = "M  file.txt\n"
        mock_subprocess_runner.run_git_command.side_effect = [
            mock_result_empty,  # git rev-parse (not empty)
            mock_result_dirty,  # git status (dirty)
        ]

        git_service.pull_repository(sample_repository)

        # Should only call git rev-parse and git status, not checkout/pull
        assert mock_subprocess_runner.run_git_command.call_count == 2

    def test_pull_repository_empty(self, git_service, sample_repository, mock_subprocess_runner):
        """Test pull skipped when repository is empty."""
        # Mock repository exists
        sample_repository.local_path.mkdir(parents=True)

        # Mock repository is empty
        mock_subprocess_runner.run_git_command.side_effect = GitOperationError("No HEAD")

        git_service.pull_repository(sample_repository)

        # Should only call git rev-parse
        assert mock_subprocess_runner.run_git_command.call_count == 1

    def test_pull_repository_not_exists(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test pull fails when repository doesn't exist."""
        with pytest.raises(GitOperationError):
            git_service.pull_repository(sample_repository)

    def test_update_remote_url(self, git_service, sample_repository, mock_subprocess_runner):
        """Test updating remote URL."""
        new_url = "git@github.com:user/test-repo.git"

        git_service.update_remote_url(sample_repository.local_path, new_url)

        mock_subprocess_runner.run_git_command.assert_called_once_with(
            ["git", "remote", "set-url", "origin", new_url],
            cwd=sample_repository.local_path,
            timeout=10,
        )

    def test_clone_or_pull_clone_scenario(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test clone_or_pull when repository doesn't exist (clone scenario)."""
        # Repository doesn't exist locally
        assert not sample_repository.exists_locally

        git_service.clone_or_pull(sample_repository, use_ssh=False)

        # Should call git clone
        mock_subprocess_runner.run_git_command.assert_called_once_with(
            [
                "git",
                "clone",
                "https://github.com/user/test-repo.git",
                str(sample_repository.local_path),
            ],
            cwd=sample_repository.local_path.parent,
            timeout=300,
        )

    def test_clone_or_pull_pull_scenario(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test clone_or_pull when repository exists (pull scenario)."""
        # Create repository directory and .git to simulate it exists
        sample_repository.local_path.mkdir(parents=True)
        (sample_repository.local_path / ".git").mkdir()

        # Mock repository is not empty and has no uncommitted changes
        mock_result = MagicMock()
        mock_result.stdout = "abc123\n"
        mock_subprocess_runner.run_git_command.side_effect = [
            mock_result,  # git rev-parse (not empty)
            MagicMock(stdout=""),  # git status (clean)
            MagicMock(),  # git checkout
            MagicMock(),  # git pull
        ]

        git_service.clone_or_pull(sample_repository, use_ssh=False)

        # Should call git commands for pull, not clone
        calls = mock_subprocess_runner.run_git_command.call_args_list
        assert len(calls) == 4
        # Verify it's doing pull operations
        assert calls[2][0][0] == ["git", "checkout", "main"]
        assert calls[3][0][0] == ["git", "pull", "origin", "main"]


class TestProtocolSwitching:
    """Test cases for protocol switching scenarios."""

    def test_ssh_to_https_protocol_switch(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test switching from SSH to HTTPS protocol."""
        # Mock current remote as SSH
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/test-repo.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Get current protocol
        current_protocol = git_service.detect_protocol(sample_repository.local_path)
        assert current_protocol == "ssh"

        # Update to HTTPS
        new_url = "https://github.com/user/test-repo.git"
        git_service.update_remote_url(sample_repository.local_path, new_url)

        # Verify remote URL was updated
        mock_subprocess_runner.run_git_command.assert_called_with(
            ["git", "remote", "set-url", "origin", new_url],
            cwd=sample_repository.local_path,
            timeout=10,
        )

    def test_https_to_ssh_protocol_switch(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test switching from HTTPS to SSH protocol."""
        # Mock current remote as HTTPS
        mock_result = MagicMock()
        mock_result.stdout = "https://github.com/user/test-repo.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Get current protocol
        current_protocol = git_service.detect_protocol(sample_repository.local_path)
        assert current_protocol == "https"

        # Update to SSH
        new_url = "git@github.com:user/test-repo.git"
        git_service.update_remote_url(sample_repository.local_path, new_url)

        # Verify remote URL was updated
        mock_subprocess_runner.run_git_command.assert_called_with(
            ["git", "remote", "set-url", "origin", new_url],
            cwd=sample_repository.local_path,
            timeout=10,
        )

    def test_no_protocol_switch_needed(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test when no protocol switch is needed."""
        # Mock current remote as HTTPS
        mock_result = MagicMock()
        mock_result.stdout = "https://github.com/user/test-repo.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Get current protocol - should match intended protocol
        current_protocol = git_service.detect_protocol(sample_repository.local_path)
        intended_protocol = "https"

        assert current_protocol == intended_protocol
        # No remote update should be needed

    def test_protocol_detection_edge_cases(
        self, git_service, sample_repository, mock_subprocess_runner
    ):
        """Test protocol detection with edge cases."""
        # Test with no remote
        mock_subprocess_runner.run_git_command.side_effect = GitOperationError("No remote")
        result = git_service.detect_protocol(sample_repository.local_path)
        assert result is None

        # Test with unusual URL format
        mock_result = MagicMock()
        mock_result.stdout = "file:///local/repo.git\n"
        mock_subprocess_runner.run_git_command.side_effect = None
        mock_subprocess_runner.run_git_command.return_value = mock_result

        result = git_service.detect_protocol(sample_repository.local_path)
        assert result is None  # Unknown protocol
