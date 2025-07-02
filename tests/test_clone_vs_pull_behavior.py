"""
Tests for clone vs pull behavior in the sync command.
Tests that the same command (sync) intelligently clones or pulls based on repository state.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from git_batch_pull.core.batch_processor import BatchProcessor
from git_batch_pull.models.repository import Repository, RepositoryInfo
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
def batch_processor(git_service):
    """BatchProcessor instance for testing."""
    return BatchProcessor(git_service)


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


class TestCloneVsPullBehavior:
    """Test cases for clone vs pull behavior in sync operations."""

    def test_sync_clones_when_repository_not_exists(
        self, batch_processor, sample_repository, mock_subprocess_runner
    ):
        """Test that sync clones when repository doesn't exist locally."""
        # Repository doesn't exist locally
        assert not sample_repository.exists_locally

        # Process the repository
        batch_processor.process_repositories([sample_repository], use_ssh=False, dry_run=False)

        # Should call git clone
        calls = mock_subprocess_runner.run_git_command.call_args_list
        clone_calls = [call for call in calls if call[0][0][0:2] == ["git", "clone"]]
        assert len(clone_calls) == 1

        # Verify clone command
        clone_call = clone_calls[0]
        assert clone_call[0][0] == [
            "git",
            "clone",
            "https://github.com/user/test-repo.git",
            str(sample_repository.local_path),
        ]

    def test_sync_clones_with_ssh_when_repository_not_exists(
        self, batch_processor, sample_repository, mock_subprocess_runner
    ):
        """Test that sync clones with SSH when repo doesn't exist and SSH requested."""
        # Repository doesn't exist locally
        assert not sample_repository.exists_locally

        # Process the repository with SSH
        batch_processor.process_repositories([sample_repository], use_ssh=True, dry_run=False)

        # Should call git clone with SSH URL
        calls = mock_subprocess_runner.run_git_command.call_args_list
        clone_calls = [call for call in calls if call[0][0][0:2] == ["git", "clone"]]
        assert len(clone_calls) == 1

        # Verify clone command uses SSH URL
        clone_call = clone_calls[0]
        assert clone_call[0][0] == [
            "git",
            "clone",
            "git@github.com:user/test-repo.git",
            str(sample_repository.local_path),
        ]

    def test_sync_pulls_when_repository_exists_clean(
        self, batch_processor, sample_repository, mock_subprocess_runner
    ):
        """Test that sync pulls when repository exists and is clean."""
        # Create repository directory to simulate it exists
        sample_repository.local_path.mkdir(parents=True)
        (sample_repository.local_path / ".git").mkdir()  # Create .git directory

        # Mock repository is not empty and has no uncommitted changes
        mock_result_head = MagicMock()
        mock_result_head.stdout = "abc123\n"
        mock_result_status = MagicMock()
        mock_result_status.stdout = ""

        mock_subprocess_runner.run_git_command.side_effect = [
            mock_result_head,  # git rev-parse (not empty)
            mock_result_status,  # git status (clean)
            MagicMock(),  # git checkout
            MagicMock(),  # git pull
        ]

        # Process the repository
        batch_processor.process_repositories([sample_repository], use_ssh=False, dry_run=False)

        # Should call git pull operations, not clone
        calls = mock_subprocess_runner.run_git_command.call_args_list
        clone_calls = [call for call in calls if call[0][0][0:2] == ["git", "clone"]]
        pull_calls = [call for call in calls if call[0][0][0:2] == ["git", "pull"]]
        checkout_calls = [call for call in calls if call[0][0][0:2] == ["git", "checkout"]]

        assert len(clone_calls) == 0  # No clone
        assert len(pull_calls) == 1  # One pull
        assert len(checkout_calls) == 1  # One checkout

        # Verify pull command
        pull_call = pull_calls[0]
        assert pull_call[0][0] == ["git", "pull", "origin", "main"]

    def test_sync_skips_pull_when_repository_has_uncommitted_changes(
        self, batch_processor, sample_repository, mock_subprocess_runner
    ):
        """Test that sync skips pull when repository exists but has uncommitted changes."""
        # Create repository directory to simulate it exists
        sample_repository.local_path.mkdir(parents=True)
        (sample_repository.local_path / ".git").mkdir()  # Create .git directory

        # Mock repository is not empty but has uncommitted changes
        mock_result_head = MagicMock()
        mock_result_head.stdout = "abc123\n"
        mock_result_status = MagicMock()
        mock_result_status.stdout = "M  file.txt\n"

        mock_subprocess_runner.run_git_command.side_effect = [
            mock_result_head,  # git rev-parse (not empty)
            mock_result_status,  # git status (dirty)
        ]

        # Process the repository
        batch_processor.process_repositories([sample_repository], use_ssh=False, dry_run=False)

        # Should not call git pull or checkout due to uncommitted changes
        calls = mock_subprocess_runner.run_git_command.call_args_list
        pull_calls = [call for call in calls if call[0][0][0:2] == ["git", "pull"]]
        checkout_calls = [call for call in calls if call[0][0][0:2] == ["git", "checkout"]]

        assert len(pull_calls) == 0  # No pull
        assert len(checkout_calls) == 0  # No checkout
        assert len(calls) == 2  # Only rev-parse and status

    def test_sync_skips_pull_when_repository_is_empty(
        self, batch_processor, sample_repository, mock_subprocess_runner
    ):
        """Test that sync skips pull when repository exists but is empty."""
        # Create repository directory to simulate it exists
        sample_repository.local_path.mkdir(parents=True)
        (sample_repository.local_path / ".git").mkdir()  # Create .git directory

        # Mock repository is empty (no HEAD)
        mock_subprocess_runner.run_git_command.side_effect = [
            Exception("No HEAD")  # git rev-parse fails
        ]

        # Process the repository
        batch_processor.process_repositories([sample_repository], use_ssh=False, dry_run=False)

        # Should not call git pull or checkout for empty repository
        calls = mock_subprocess_runner.run_git_command.call_args_list
        pull_calls = [call for call in calls if call[0][0][0:2] == ["git", "pull"]]
        checkout_calls = [call for call in calls if call[0][0][0:2] == ["git", "checkout"]]

        assert len(pull_calls) == 0  # No pull
        assert len(checkout_calls) == 0  # No checkout
        assert len(calls) == 1  # Only rev-parse

    def test_sync_mixed_repositories_clone_and_pull(
        self, batch_processor, temp_base_folder, mock_subprocess_runner
    ):
        """Test sync with mixed repositories - some to clone, some to pull."""
        # Create multiple repositories
        repo1_info = RepositoryInfo(
            name="new-repo",
            clone_url="https://github.com/user/new-repo.git",
            ssh_url="git@github.com:user/new-repo.git",
            default_branch="main",
            private=False,
            fork=False,
            archived=False,
        )
        repo1 = Repository(info=repo1_info, local_path=temp_base_folder / "new-repo")

        repo2_info = RepositoryInfo(
            name="existing-repo",
            clone_url="https://github.com/user/existing-repo.git",
            ssh_url="git@github.com:user/existing-repo.git",
            default_branch="main",
            private=False,
            fork=False,
            archived=False,
        )
        repo2 = Repository(info=repo2_info, local_path=temp_base_folder / "existing-repo")

        # Create existing repository directory
        repo2.local_path.mkdir(parents=True)
        (repo2.local_path / ".git").mkdir()  # Create .git directory

        # Mock responses for existing repository
        def mock_git_command(command, **kwargs):
            if kwargs.get("cwd") == repo2.local_path:
                if command[0:2] == ["git", "rev-parse"]:
                    mock_result = MagicMock()
                    mock_result.stdout = "abc123\n"
                    return mock_result
                elif command[0:2] == ["git", "status"]:
                    mock_result = MagicMock()
                    mock_result.stdout = ""
                    return mock_result
                else:
                    return MagicMock()
            else:
                return MagicMock()

        mock_subprocess_runner.run_git_command.side_effect = mock_git_command

        # Process both repositories
        batch_processor.process_repositories([repo1, repo2], use_ssh=False, dry_run=False)

        calls = mock_subprocess_runner.run_git_command.call_args_list

        # Should have clone calls for new repository
        clone_calls = [call for call in calls if call[0][0][0:2] == ["git", "clone"]]
        assert len(clone_calls) == 1
        assert "new-repo" in str(clone_calls[0][0][0])

        # Should have pull calls for existing repository
        pull_calls = [call for call in calls if call[0][0][0:2] == ["git", "pull"]]
        assert len(pull_calls) == 1

    def test_sync_dry_run_shows_intended_actions(
        self, batch_processor, sample_repository, mock_subprocess_runner
    ):
        """Test that sync in dry run mode shows intended actions without executing them."""
        # Repository doesn't exist locally
        assert not sample_repository.exists_locally

        # Process the repository in dry run mode
        batch_processor.process_repositories([sample_repository], use_ssh=False, dry_run=True)

        # Should not call any git commands in dry run
        calls = mock_subprocess_runner.run_git_command.call_args_list
        assert len(calls) == 0

    def test_sync_respects_ssh_preference_for_existing_repos(
        self, batch_processor, sample_repository, mock_subprocess_runner
    ):
        """Test that sync pulls existing repositories regardless of SSH preference."""
        # Create repository directory to simulate it exists
        sample_repository.local_path.mkdir(parents=True)
        (sample_repository.local_path / ".git").mkdir()  # Create .git directory

        # Mock repository is not empty, clean
        mock_result_head = MagicMock()
        mock_result_head.stdout = "abc123\n"
        mock_result_status = MagicMock()
        mock_result_status.stdout = ""

        def mock_git_command(command, **kwargs):
            if command[0:2] == ["git", "rev-parse"]:
                return mock_result_head
            elif command[0:2] == ["git", "status"]:
                return mock_result_status
            else:
                return MagicMock()

        mock_subprocess_runner.run_git_command.side_effect = mock_git_command

        # Process the repository with SSH preference (should still pull)
        batch_processor.process_repositories([sample_repository], use_ssh=True, dry_run=False)

        calls = mock_subprocess_runner.run_git_command.call_args_list

        # Should pull the existing repository
        pull_calls = [call for call in calls if call[0][0][0:2] == ["git", "pull"]]
        assert len(pull_calls) == 1

    def test_sync_handles_git_errors_gracefully(
        self, batch_processor, sample_repository, mock_subprocess_runner
    ):
        """Test that sync handles git errors gracefully."""
        # Repository doesn't exist locally
        assert not sample_repository.exists_locally

        # Mock git clone to fail
        mock_subprocess_runner.run_git_command.side_effect = Exception("Git error")

        # Process the repository - should not crash
        result = batch_processor.process_repositories(
            [sample_repository], use_ssh=False, dry_run=False
        )

        # Should handle error gracefully
        assert result.failed == 1
        assert result.processed == 0
        assert len(result.errors) == 1

    def test_sync_with_different_default_branches(
        self, batch_processor, temp_base_folder, mock_subprocess_runner
    ):
        """Test sync with repositories having different default branches."""
        # Create repository with non-main default branch
        repo_info = RepositoryInfo(
            name="develop-repo",
            clone_url="https://github.com/user/develop-repo.git",
            ssh_url="git@github.com:user/develop-repo.git",
            default_branch="develop",  # Not main
            private=False,
            fork=False,
            archived=False,
        )
        repo = Repository(info=repo_info, local_path=temp_base_folder / "develop-repo")

        # Create repository directory to simulate it exists
        repo.local_path.mkdir(parents=True)
        (repo.local_path / ".git").mkdir()  # Create .git directory

        # Mock repository is not empty and clean
        mock_result_head = MagicMock()
        mock_result_head.stdout = "abc123\n"
        mock_result_status = MagicMock()
        mock_result_status.stdout = ""

        mock_subprocess_runner.run_git_command.side_effect = [
            mock_result_head,  # git rev-parse
            mock_result_status,  # git status
            MagicMock(),  # git checkout
            MagicMock(),  # git pull
        ]

        # Process the repository
        batch_processor.process_repositories([repo], use_ssh=False, dry_run=False)

        calls = mock_subprocess_runner.run_git_command.call_args_list

        # Should checkout and pull from develop branch
        checkout_calls = [call for call in calls if call[0][0][0:2] == ["git", "checkout"]]
        pull_calls = [call for call in calls if call[0][0][0:2] == ["git", "pull"]]

        assert len(checkout_calls) == 1
        assert checkout_calls[0][0][0] == ["git", "checkout", "develop"]

        assert len(pull_calls) == 1
        assert pull_calls[0][0][0] == ["git", "pull", "origin", "develop"]
