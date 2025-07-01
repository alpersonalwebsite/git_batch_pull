"""
Integration tests for protocol switching with user interaction.
Tests the complete workflow of detecting mismatches and prompting users.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from git_batch_pull.core.protocol_handler import ProtocolHandler
from git_batch_pull.models.repository import Repository, RepositoryBatch, RepositoryInfo
from git_batch_pull.security import PathValidator, SafeSubprocessRunner
from git_batch_pull.services.git_service import GitService
from git_batch_pull.services.github_service import GitHubService
from git_batch_pull.services.repository_service import RepositoryService


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
def mock_github_service():
    """Mock GitHubService for testing."""
    return MagicMock(spec=GitHubService)


@pytest.fixture
def git_service(temp_base_folder, mock_subprocess_runner, path_validator):
    """GitService instance for testing."""
    return GitService(temp_base_folder, mock_subprocess_runner, path_validator)


@pytest.fixture
def repository_service(temp_base_folder, git_service, mock_github_service):
    """RepositoryService instance for testing."""
    store_path = temp_base_folder / "repo_cache.json"
    return RepositoryService(store_path, mock_github_service, git_service)


@pytest.fixture
def protocol_handler(repository_service):
    """ProtocolHandler instance for testing."""
    return ProtocolHandler(repository_service)


@pytest.fixture
def sample_repositories(temp_base_folder):
    """Create sample repositories for testing."""
    repositories = []

    # Repository 1: Currently using SSH
    repo1_info = RepositoryInfo(
        name="repo-ssh",
        clone_url="https://github.com/user/repo-ssh.git",
        ssh_url="git@github.com:user/repo-ssh.git",
        default_branch="main",
        private=False,
        fork=False,
        archived=False,
    )
    repo1 = Repository(info=repo1_info, local_path=temp_base_folder / "repo-ssh")

    # Repository 2: Currently using HTTPS
    repo2_info = RepositoryInfo(
        name="repo-https",
        clone_url="https://github.com/user/repo-https.git",
        ssh_url="git@github.com:user/repo-https.git",
        default_branch="main",
        private=False,
        fork=False,
        archived=False,
    )
    repo2 = Repository(info=repo2_info, local_path=temp_base_folder / "repo-https")

    repositories.extend([repo1, repo2])
    return repositories


class TestProtocolSwitchingIntegration:
    """Integration tests for protocol switching scenarios."""

    def test_detect_ssh_to_https_mismatch(
        self, repository_service, sample_repositories, mock_subprocess_runner
    ):
        """Test detecting SSH to HTTPS protocol mismatch."""
        # Mock repository exists and current remote is SSH
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return SSH URL
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Detect mismatches when intending to use HTTPS
        batch = RepositoryBatch(
            repositories=sample_repositories, entity_type="user", entity_name="user"
        )
        mismatches = repository_service.detect_protocol_mismatches(batch, "https")

        # Should detect mismatch for SSH repository
        assert len(mismatches) == 1
        assert mismatches[0][0] == "repo-ssh"
        assert "git@github.com:user/repo-ssh.git" in mismatches[0][1]

    def test_detect_https_to_ssh_mismatch(
        self, repository_service, sample_repositories, mock_subprocess_runner
    ):
        """Test detecting HTTPS to SSH protocol mismatch."""
        # Mock repository exists and current remote is HTTPS
        sample_repositories[1].local_path.mkdir(parents=True)
        (sample_repositories[1].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return HTTPS URL
        mock_result = MagicMock()
        mock_result.stdout = "https://github.com/user/repo-https.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Detect mismatches when intending to use SSH
        mismatches = repository_service.detect_protocol_mismatches(sample_repositories, "ssh")

        # Should detect mismatch for HTTPS repository
        assert len(mismatches) == 1
        assert mismatches[0][0] == "repo-https"
        assert "https://github.com/user/repo-https.git" in mismatches[0][1]

    def test_no_mismatch_when_protocols_align(
        self, repository_service, sample_repositories, mock_subprocess_runner
    ):
        """Test no mismatch detected when protocols align."""
        # Mock repository exists and current remote is SSH
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return SSH URL
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Detect mismatches when intending to use SSH (should match)
        batch = RepositoryBatch(
            repositories=sample_repositories, entity_type="user", entity_name="user"
        )
        mismatches = repository_service.detect_protocol_mismatches(batch, "ssh")

        # Should not detect any mismatches
        assert len(mismatches) == 0

    def test_fix_protocol_mismatch_ssh_to_https(
        self, repository_service, sample_repositories, mock_subprocess_runner
    ):
        """Test fixing SSH to HTTPS protocol mismatch."""
        # Mock repository exists
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock current remote as SSH
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Fix protocol mismatches to HTTPS
        batch = RepositoryBatch(
            repositories=sample_repositories, entity_type="user", entity_name="user"
        )
        repository_service.fix_protocol_mismatches(batch, "https", "user")

        # Verify remote URL was updated to HTTPS
        calls = mock_subprocess_runner.run_git_command.call_args_list
        # Should have called git remote get-url and git remote set-url
        assert len(calls) >= 2

        # Find the set-url call
        set_url_call = None
        for call in calls:
            if call[0][0][0:3] == ["git", "remote", "set-url"]:
                set_url_call = call
                break

        assert set_url_call is not None
        assert set_url_call[0][0] == [
            "git",
            "remote",
            "set-url",
            "origin",
            "https://github.com/user/repo-ssh.git",
        ]

    def test_fix_protocol_mismatch_https_to_ssh(
        self, repository_service, sample_repositories, mock_subprocess_runner
    ):
        """Test fixing HTTPS to SSH protocol mismatch."""
        # Mock repository exists
        sample_repositories[1].local_path.mkdir(parents=True)
        (sample_repositories[1].local_path / ".git").mkdir()  # Create .git directory

        # Mock current remote as HTTPS
        mock_result = MagicMock()
        mock_result.stdout = "https://github.com/user/repo-https.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Fix protocol mismatches to SSH
        batch = RepositoryBatch(
            repositories=sample_repositories, entity_type="user", entity_name="user"
        )
        repository_service.fix_protocol_mismatches(batch, "ssh", "user")

        # Verify remote URL was updated to SSH
        calls = mock_subprocess_runner.run_git_command.call_args_list
        # Should have called git remote get-url and git remote set-url
        assert len(calls) >= 2

        # Find the set-url call
        set_url_call = None
        for call in calls:
            if call[0][0][0:3] == ["git", "remote", "set-url"]:
                set_url_call = call
                break

        assert set_url_call is not None
        assert set_url_call[0][0] == [
            "git",
            "remote",
            "set-url",
            "origin",
            "git@github.com:user/repo-https.git",
        ]

    @patch("builtins.input")
    def test_protocol_handler_user_chooses_to_switch(
        self, mock_input, protocol_handler, sample_repositories, mock_subprocess_runner
    ):
        """Test protocol handler when user chooses to switch protocols."""
        # Mock user input to choose option 1 (switch)
        mock_input.return_value = "1"

        # Mock repository exists and current remote is SSH
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return SSH URL
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Handle protocol mismatches
        result = protocol_handler.handle_protocol_mismatches(
            sample_repositories, "https", "user", dry_run=False
        )

        # Should return True (protocol switch occurred)
        assert result is True

        # Verify user was prompted
        mock_input.assert_called_once()

        # Verify remote URL update was attempted
        calls = mock_subprocess_runner.run_git_command.call_args_list
        assert len(calls) >= 2

    @patch("builtins.input")
    def test_protocol_handler_user_chooses_not_to_switch(
        self, mock_input, protocol_handler, sample_repositories, mock_subprocess_runner
    ):
        """Test protocol handler when user chooses NOT to switch protocols."""
        # Mock user input to choose option 2 (don't switch)
        mock_input.return_value = "2"

        # Mock repository exists and current remote is SSH
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return SSH URL
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Handle protocol mismatches
        result = protocol_handler.handle_protocol_mismatches(
            sample_repositories, "https", "user", dry_run=False
        )

        # Should return False (no protocol switch)
        assert result is False

        # Verify user was prompted
        mock_input.assert_called_once()

        # Should only call git remote get-url, not set-url
        calls = mock_subprocess_runner.run_git_command.call_args_list
        set_url_calls = [call for call in calls if call[0][0][0:3] == ["git", "remote", "set-url"]]
        assert len(set_url_calls) == 0

    @patch("builtins.input")
    def test_protocol_handler_user_cancels(
        self, mock_input, protocol_handler, sample_repositories, mock_subprocess_runner
    ):
        """Test protocol handler when user cancels (KeyboardInterrupt)."""
        # Mock user input to raise KeyboardInterrupt
        mock_input.side_effect = KeyboardInterrupt()

        # Mock repository exists and current remote is SSH
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return SSH URL
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Handle protocol mismatches
        result = protocol_handler.handle_protocol_mismatches(
            sample_repositories, "https", "user", dry_run=False
        )

        # Should return False (no protocol switch due to cancellation)
        assert result is False

        # Verify user was prompted
        mock_input.assert_called_once()

    def test_protocol_handler_dry_run(
        self, protocol_handler, sample_repositories, mock_subprocess_runner
    ):
        """Test protocol handler in dry run mode."""
        # Mock repository exists and current remote is SSH
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return SSH URL
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Handle protocol mismatches in dry run mode
        result = protocol_handler.handle_protocol_mismatches(
            sample_repositories, "https", "user", dry_run=True
        )

        # Should return True (would have switched)
        assert result is True

        # Should only call git remote get-url, not set-url (dry run)
        calls = mock_subprocess_runner.run_git_command.call_args_list
        set_url_calls = [call for call in calls if call[0][0][0:3] == ["git", "remote", "set-url"]]
        assert len(set_url_calls) == 0

    def test_protocol_handler_no_mismatches(
        self, protocol_handler, sample_repositories, mock_subprocess_runner
    ):
        """Test protocol handler when no mismatches are detected."""
        # Mock repository exists and current remote is SSH
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return SSH URL
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Handle protocol mismatches when using SSH (should match)
        result = protocol_handler.handle_protocol_mismatches(
            sample_repositories,
            "ssh",
            "user",
            dry_run=False,  # Matches the current protocol
        )

        # Should return True (no action needed)
        assert result is True

        # Should only call git remote get-url
        calls = mock_subprocess_runner.run_git_command.call_args_list
        set_url_calls = [call for call in calls if call[0][0][0:3] == ["git", "remote", "set-url"]]
        assert len(set_url_calls) == 0

    @patch("builtins.input")
    def test_protocol_handler_invalid_input_then_valid(
        self, mock_input, protocol_handler, sample_repositories, mock_subprocess_runner
    ):
        """Test protocol handler with invalid input followed by valid input."""
        # Mock user input to provide invalid input first, then valid
        mock_input.side_effect = ["invalid", "3", "1"]  # invalid, invalid, then valid

        # Mock repository exists and current remote is SSH
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory

        # Mock git remote get-url to return SSH URL
        mock_result = MagicMock()
        mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
        mock_subprocess_runner.run_git_command.return_value = mock_result

        # Handle protocol mismatches
        result = protocol_handler.handle_protocol_mismatches(
            sample_repositories, "https", "user", dry_run=False
        )

        # Should return True (protocol switch occurred)
        assert result is True

        # Verify user was prompted multiple times
        assert mock_input.call_count == 3

    def test_multiple_repositories_mixed_protocols(
        self, repository_service, sample_repositories, mock_subprocess_runner
    ):
        """Test handling multiple repositories with different protocols."""
        # Mock both repositories exist
        sample_repositories[0].local_path.mkdir(parents=True)
        (sample_repositories[0].local_path / ".git").mkdir()  # Create .git directory
        sample_repositories[1].local_path.mkdir(parents=True)
        (sample_repositories[1].local_path / ".git").mkdir()  # Create .git directory

        # Mock different protocols for each repository
        def mock_git_command(command, **kwargs):
            if kwargs.get("cwd") == sample_repositories[0].local_path:
                # First repo uses SSH
                mock_result = MagicMock()
                mock_result.stdout = "git@github.com:user/repo-ssh.git\n"
                return mock_result
            elif kwargs.get("cwd") == sample_repositories[1].local_path:
                # Second repo uses HTTPS
                mock_result = MagicMock()
                mock_result.stdout = "https://github.com/user/repo-https.git\n"
                return mock_result
            else:
                return MagicMock()

        mock_subprocess_runner.run_git_command.side_effect = mock_git_command

        # Detect mismatches when intending to use SSH
        batch = RepositoryBatch(
            repositories=sample_repositories, entity_type="user", entity_name="user"
        )
        mismatches = repository_service.detect_protocol_mismatches(batch, "ssh")

        # Should detect mismatch only for HTTPS repository
        assert len(mismatches) == 1
        assert mismatches[0][0] == "repo-https"
        assert "https://github.com/user/repo-https.git" in mismatches[0][1]
