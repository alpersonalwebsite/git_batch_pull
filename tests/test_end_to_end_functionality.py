"""
Simple end-to-end tests for the core functionality.
Tests clone vs pull behavior and protocol switching in realistic scenarios.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from git_batch_pull.models.repository import Repository, RepositoryInfo
from git_batch_pull.security import PathValidator, SafeSubprocessRunner
from git_batch_pull.services.git_service import GitService


class TestEndToEndFunctionality:
    """End-to-end tests for core functionality."""

    def test_sync_functionality_clone_scenario(self):
        """Test that sync clones when repository doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            # Create test repository
            repo_info = RepositoryInfo(
                name="test-repo",
                clone_url="https://github.com/user/test-repo.git",
                ssh_url="git@github.com:user/test-repo.git",
                default_branch="main",
                private=False,
                fork=False,
                archived=False,
            )
            repo = Repository(info=repo_info, local_path=base_folder / "test-repo")

            # Repository doesn't exist - should clone
            assert not repo.exists_locally

            # Call clone_or_pull (core sync functionality)
            git_service.clone_or_pull(repo, use_ssh=False)

            # Should have called git clone with HTTPS URL
            mock_runner.run_git_command.assert_called_once_with(
                ["git", "clone", "https://github.com/user/test-repo.git", str(repo.local_path)],
                cwd=repo.local_path.parent,
                timeout=300,
            )

    def test_sync_functionality_pull_scenario(self):
        """Test that sync pulls when repository exists and is clean."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            # Create test repository
            repo_info = RepositoryInfo(
                name="test-repo",
                clone_url="https://github.com/user/test-repo.git",
                ssh_url="git@github.com:user/test-repo.git",
                default_branch="main",
                private=False,
                fork=False,
                archived=False,
            )
            repo_path = base_folder / "test-repo"
            repo = Repository(info=repo_info, local_path=repo_path)

            # Create repository directory and .git to simulate existing repo
            repo_path.mkdir(parents=True)
            (repo_path / ".git").mkdir()

            # Repository exists - should pull
            assert repo.exists_locally

            # Mock git commands for pull scenario
            mock_head_result = MagicMock()
            mock_head_result.stdout = "abc123\n"
            mock_status_result = MagicMock()
            mock_status_result.stdout = ""  # Clean repository

            mock_runner.run_git_command.side_effect = [
                mock_head_result,  # git rev-parse (not empty)
                mock_status_result,  # git status (clean)
                MagicMock(),  # git checkout
                MagicMock(),  # git pull
            ]

            # Call clone_or_pull (core sync functionality)
            git_service.clone_or_pull(repo, use_ssh=False)

            # Should have called pull commands, not clone
            calls = mock_runner.run_git_command.call_args_list
            assert len(calls) == 4

            # Check that checkout and pull were called
            checkout_call = calls[2]
            pull_call = calls[3]

            assert checkout_call[0][0] == ["git", "checkout", "main"]
            assert pull_call[0][0] == ["git", "pull", "origin", "main"]

    def test_protocol_detection_ssh(self):
        """Test SSH protocol detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            # Mock git remote get-url to return SSH URL
            mock_result = MagicMock()
            mock_result.stdout = "git@github.com:user/test-repo.git\n"
            mock_runner.run_git_command.return_value = mock_result

            repo_path = base_folder / "test-repo"
            protocol = git_service.detect_protocol(repo_path)

            assert protocol == "ssh"

    def test_protocol_detection_https(self):
        """Test HTTPS protocol detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            # Mock git remote get-url to return HTTPS URL
            mock_result = MagicMock()
            mock_result.stdout = "https://github.com/user/test-repo.git\n"
            mock_runner.run_git_command.return_value = mock_result

            repo_path = base_folder / "test-repo"
            protocol = git_service.detect_protocol(repo_path)

            assert protocol == "https"

    def test_protocol_switching_ssh_to_https(self):
        """Test switching from SSH to HTTPS protocol."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            repo_path = base_folder / "test-repo"
            new_url = "https://github.com/user/test-repo.git"

            # Update remote URL (protocol switch)
            git_service.update_remote_url(repo_path, new_url)

            # Should have called git remote set-url
            mock_runner.run_git_command.assert_called_once_with(
                ["git", "remote", "set-url", "origin", new_url], cwd=repo_path, timeout=10
            )

    def test_protocol_switching_https_to_ssh(self):
        """Test switching from HTTPS to SSH protocol."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            repo_path = base_folder / "test-repo"
            new_url = "git@github.com:user/test-repo.git"

            # Update remote URL (protocol switch)
            git_service.update_remote_url(repo_path, new_url)

            # Should have called git remote set-url
            mock_runner.run_git_command.assert_called_once_with(
                ["git", "remote", "set-url", "origin", new_url], cwd=repo_path, timeout=10
            )

    def test_sync_with_ssh_flag_clones_with_ssh(self):
        """Test that sync with SSH flag clones using SSH URL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            # Create test repository
            repo_info = RepositoryInfo(
                name="test-repo",
                clone_url="https://github.com/user/test-repo.git",
                ssh_url="git@github.com:user/test-repo.git",
                default_branch="main",
                private=False,
                fork=False,
                archived=False,
            )
            repo = Repository(info=repo_info, local_path=base_folder / "test-repo")

            # Repository doesn't exist - should clone with SSH
            assert not repo.exists_locally

            # Call clone_or_pull with SSH flag
            git_service.clone_or_pull(repo, use_ssh=True)

            # Should have called git clone with SSH URL
            mock_runner.run_git_command.assert_called_once_with(
                ["git", "clone", "git@github.com:user/test-repo.git", str(repo.local_path)],
                cwd=repo.local_path.parent,
                timeout=300,
            )

    def test_sync_skips_pull_when_uncommitted_changes(self):
        """Test that sync skips pull when repository has uncommitted changes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            # Create test repository
            repo_info = RepositoryInfo(
                name="test-repo",
                clone_url="https://github.com/user/test-repo.git",
                ssh_url="git@github.com:user/test-repo.git",
                default_branch="main",
                private=False,
                fork=False,
                archived=False,
            )
            repo_path = base_folder / "test-repo"
            repo = Repository(info=repo_info, local_path=repo_path)

            # Create repository directory and .git to simulate existing repo
            repo_path.mkdir(parents=True)
            (repo_path / ".git").mkdir()

            # Mock git commands - repository has uncommitted changes
            mock_head_result = MagicMock()
            mock_head_result.stdout = "abc123\n"
            mock_status_result = MagicMock()
            mock_status_result.stdout = "M  file.txt\n"  # Dirty repository

            mock_runner.run_git_command.side_effect = [
                mock_head_result,  # git rev-parse (not empty)
                mock_status_result,  # git status (dirty)
            ]

            # Call clone_or_pull - should skip pull due to uncommitted changes
            git_service.clone_or_pull(repo, use_ssh=False)

            # Should only call rev-parse and status, not checkout/pull
            calls = mock_runner.run_git_command.call_args_list
            assert len(calls) == 2

            # Verify no checkout or pull was attempted
            for call in calls:
                assert call[0][0][0:2] not in [["git", "checkout"], ["git", "pull"]]

    def test_sync_handles_different_default_branches(self):
        """Test that sync works with repositories having non-main default branches."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_folder = Path(temp_dir)
            mock_runner = MagicMock(spec=SafeSubprocessRunner)
            validator = PathValidator()

            git_service = GitService(base_folder, mock_runner, validator)

            # Create test repository with develop as default branch
            repo_info = RepositoryInfo(
                name="test-repo",
                clone_url="https://github.com/user/test-repo.git",
                ssh_url="git@github.com:user/test-repo.git",
                default_branch="develop",  # Not main
                private=False,
                fork=False,
                archived=False,
            )
            repo_path = base_folder / "test-repo"
            repo = Repository(info=repo_info, local_path=repo_path)

            # Create repository directory and .git to simulate existing repo
            repo_path.mkdir(parents=True)
            (repo_path / ".git").mkdir()

            # Mock git commands for pull scenario
            mock_head_result = MagicMock()
            mock_head_result.stdout = "abc123\n"
            mock_status_result = MagicMock()
            mock_status_result.stdout = ""  # Clean repository

            mock_runner.run_git_command.side_effect = [
                mock_head_result,  # git rev-parse (not empty)
                mock_status_result,  # git status (clean)
                MagicMock(),  # git checkout
                MagicMock(),  # git pull
            ]

            # Call clone_or_pull
            git_service.clone_or_pull(repo, use_ssh=False)

            calls = mock_runner.run_git_command.call_args_list

            # Should checkout and pull from develop branch
            checkout_call = calls[2]
            pull_call = calls[3]

            assert checkout_call[0][0] == ["git", "checkout", "develop"]
            assert pull_call[0][0] == ["git", "pull", "origin", "develop"]
