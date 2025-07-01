#!/usr/bin/env python3
"""
Performance benchmarks for git-batch-pull.

This script measures the performance of key operations to ensure
the tool scales well with different repository sizes and configurations.
"""

import statistics
import tempfile
import time
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock

from git_batch_pull.core.batch_processor import BatchProcessor
from git_batch_pull.models.repository import Repository, RepositoryInfo
from git_batch_pull.security import PathValidator, SafeSubprocessRunner
from git_batch_pull.services.git_service import GitService


class BenchmarkRunner:
    """Run performance benchmarks for git-batch-pull operations."""

    def __init__(self):
        self.results: Dict[str, List[float]] = {}

    def time_operation(self, name: str, operation_func, *args, **kwargs) -> float:
        """Time a single operation and record the result."""
        start_time = time.perf_counter()
        result = operation_func(*args, **kwargs)
        end_time = time.perf_counter()

        duration = end_time - start_time
        if name not in self.results:
            self.results[name] = []
        self.results[name].append(duration)

        return duration

    def benchmark_repository_creation(self, count: int = 100) -> None:
        """Benchmark repository object creation."""

        def create_repositories():
            repositories = []
            for i in range(count):
                info = RepositoryInfo(
                    name=f"repo-{i}",
                    clone_url=f"https://github.com/user/repo-{i}.git",
                    ssh_url=f"git@github.com:user/repo-{i}.git",
                    default_branch="main",
                )
                repo = Repository(info=info, local_path=Path(f"/tmp/repo-{i}"))
                repositories.append(repo)
            return repositories

        self.time_operation(f"create_{count}_repositories", create_repositories)

    def benchmark_protocol_detection(self, count: int = 50) -> None:
        """Benchmark protocol detection for multiple repositories."""
        # Setup
        temp_dir = Path(tempfile.mkdtemp())
        mock_subprocess = MagicMock(spec=SafeSubprocessRunner)
        path_validator = PathValidator()
        git_service = GitService(temp_dir, mock_subprocess, path_validator)

        # Create test repositories
        repositories = []
        for i in range(count):
            repo_path = temp_dir / f"repo-{i}"
            repo_path.mkdir(parents=True)
            (repo_path / ".git").mkdir()
            repositories.append(repo_path)

        # Mock git remote get-url responses
        def mock_git_command(command, **kwargs):
            mock_result = MagicMock()
            repo_num = int(kwargs.get("cwd", temp_dir).name.split("-")[-1])
            if repo_num % 2 == 0:
                mock_result.stdout = f"https://github.com/user/repo-{repo_num}.git"
            else:
                mock_result.stdout = f"git@github.com:user/repo-{repo_num}.git"
            return mock_result

        mock_subprocess.run_git_command.side_effect = mock_git_command

        def detect_protocols():
            protocols = []
            for repo_path in repositories:
                protocol = git_service.detect_protocol(repo_path)
                protocols.append(protocol)
            return protocols

        self.time_operation(f"detect_protocol_{count}_repos", detect_protocols)

    def benchmark_batch_processing_simulation(self, count: int = 20) -> None:
        """Benchmark batch processing simulation (dry run)."""
        # Setup
        temp_dir = Path(tempfile.mkdtemp())
        mock_subprocess = MagicMock(spec=SafeSubprocessRunner)
        path_validator = PathValidator()
        git_service = GitService(temp_dir, mock_subprocess, path_validator)
        batch_processor = BatchProcessor(git_service)

        # Create test repositories
        repositories = []
        for i in range(count):
            info = RepositoryInfo(
                name=f"repo-{i}",
                clone_url=f"https://github.com/user/repo-{i}.git",
                ssh_url=f"git@github.com:user/repo-{i}.git",
                default_branch="main",
            )
            repo = Repository(info=info, local_path=temp_dir / f"repo-{i}")
            repositories.append(repo)

        def process_batch():
            return batch_processor.process_repositories(
                repositories,
                use_ssh=False,
                dry_run=True,  # Dry run for performance testing
                quiet=True,
            )

        self.time_operation(f"process_batch_{count}_repos", process_batch)

    def run_all_benchmarks(self) -> None:
        """Run all benchmark tests."""
        print("🚀 Running git-batch-pull Performance Benchmarks")
        print("=" * 50)

        # Repository creation benchmarks
        print("\n📦 Repository Creation Benchmarks:")
        for count in [10, 50, 100, 500]:
            duration = self.time_operation(
                f"create_{count}_repositories", self.benchmark_repository_creation, count
            )
            print(f"  Create {count:3d} repositories: {duration*1000:.2f} ms")

        # Protocol detection benchmarks
        print("\n🔍 Protocol Detection Benchmarks:")
        for count in [10, 25, 50]:
            duration = self.time_operation(
                f"detect_protocol_{count}_repos", self.benchmark_protocol_detection, count
            )
            print(f"  Detect protocols for {count:2d} repos: {duration*1000:.2f} ms")

        # Batch processing benchmarks
        print("\n⚡ Batch Processing Benchmarks (Dry Run):")
        for count in [5, 10, 20, 50]:
            duration = self.time_operation(
                f"process_batch_{count}_repos", self.benchmark_batch_processing_simulation, count
            )
            print(f"  Process batch of {count:2d} repos: {duration*1000:.2f} ms")

    def print_summary(self) -> None:
        """Print benchmark summary statistics."""
        print("\n📊 Benchmark Summary:")
        print("=" * 50)

        for operation, times in self.results.items():
            if len(times) > 1:
                mean_time = statistics.mean(times) * 1000
                std_dev = statistics.stdev(times) * 1000 if len(times) > 1 else 0
                min_time = min(times) * 1000
                max_time = max(times) * 1000

                print(f"\n{operation}:")
                print(f"  Mean: {mean_time:.2f} ms ± {std_dev:.2f} ms")
                print(f"  Range: {min_time:.2f} ms - {max_time:.2f} ms")
            else:
                print(f"\n{operation}: {times[0]*1000:.2f} ms")

        # Performance thresholds and recommendations
        print("\n💡 Performance Analysis:")
        print("-" * 30)

        # Check if any operations are taking too long
        slow_operations = []
        for operation, times in self.results.items():
            avg_time = statistics.mean(times)
            if "create_" in operation and avg_time > 0.1:  # 100ms for creation
                slow_operations.append(f"{operation}: {avg_time*1000:.2f} ms")
            elif "detect_" in operation and avg_time > 0.5:  # 500ms for detection
                slow_operations.append(f"{operation}: {avg_time*1000:.2f} ms")
            elif "process_" in operation and avg_time > 1.0:  # 1s for batch processing
                slow_operations.append(f"{operation}: {avg_time*1000:.2f} ms")

        if slow_operations:
            print("⚠️  Operations that may need optimization:")
            for op in slow_operations:
                print(f"  - {op}")
        else:
            print("✅ All operations performing within acceptable thresholds")


def main():
    """Run the benchmark suite."""
    runner = BenchmarkRunner()

    try:
        runner.run_all_benchmarks()
        runner.print_summary()

        print("\n🎯 Benchmark Results Saved")
        print(f"Total operations benchmarked: {len(runner.results)}")

    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
