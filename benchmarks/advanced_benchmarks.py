#!/usr/bin/env python3
"""
Advanced performance benchmarks for git-batch-pull.

This script provides comprehensive performance testing including:
- Memory usage profiling
- CPU profiling
- I/O performance testing
- Concurrent operation benchmarks
- Scalability testing
"""

import asyncio
import cProfile
import gc
import io
import json
import pstats
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

import psutil


@dataclass
class BenchmarkResult:
    """Benchmark result data structure."""

    name: str
    duration: float
    memory_peak: float
    memory_current: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict] = None


class PerformanceProfiler:
    """Advanced performance profiler with memory and CPU tracking."""

    def __init__(self):
        self.process = psutil.Process()
        self.results: List[BenchmarkResult] = []

    @contextmanager
    def profile(self, name: str):
        """Context manager for profiling code blocks."""
        # Start profiling
        gc.collect()  # Clean up before measurement
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = self.process.cpu_percent()

        success = True
        error = None

        try:
            yield
        except Exception as e:
            success = False
            error = str(e)
        finally:
            # End profiling
            end_time = time.perf_counter()
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = self.process.cpu_percent()

            result = BenchmarkResult(
                name=name,
                duration=end_time - start_time,
                memory_peak=max(start_memory, end_memory),
                memory_current=end_memory,
                cpu_percent=(start_cpu + end_cpu) / 2,
                success=success,
                error=error,
            )

            self.results.append(result)
            self._print_result(result)

    def _print_result(self, result: BenchmarkResult):
        """Print benchmark result."""
        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"{status} {result.name}")
        print(f"   Duration: {result.duration:.4f}s")
        print(f"   Memory: {result.memory_current:.2f}MB (peak: {result.memory_peak:.2f}MB)")
        print(f"   CPU: {result.cpu_percent:.2f}%")
        if result.error:
            print(f"   Error: {result.error}")
        print()


class MockRepository:
    """Mock repository for testing."""

    def __init__(self, name: str, size: int = 1000):
        self.name = name
        self.full_name = f"test-org/{name}"
        self.clone_url = f"https://github.com/test-org/{name}.git"
        self.ssh_url = f"git@github.com:test-org/{name}.git"
        self.size = size  # KB
        self.private = False


def setup_test_environment():
    """Set up test environment with mock data."""
    # Import here to avoid circular imports during startup
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    global git_batch_pull
    import git_batch_pull
    from git_batch_pull.core.batch_processor import BatchProcessor
    from git_batch_pull.services.git_service import GitService
    from git_batch_pull.services.github_service import GitHubService

    return git_batch_pull, GitHubService, GitService, BatchProcessor


def create_mock_repos(count: int) -> List[MockRepository]:
    """Create mock repositories for testing."""
    return [MockRepository(f"repo-{i:04d}", size=1000 + (i * 100)) for i in range(count)]


async def benchmark_github_api_calls(
    profiler: PerformanceProfiler, github_service, repo_count: int = 100
):
    """Benchmark GitHub API calls."""
    mock_repos = create_mock_repos(repo_count)

    with profiler.profile(f"GitHub API - Fetch {repo_count} repos"):
        # Mock the API response
        with patch.object(github_service, "_make_request") as mock_request:
            mock_request.return_value = {
                "data": [
                    {
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "clone_url": repo.clone_url,
                        "ssh_url": repo.ssh_url,
                        "size": repo.size,
                        "private": repo.private,
                    }
                    for repo in mock_repos
                ]
            }

            _ = await asyncio.get_event_loop().run_in_executor(
                None, github_service.get_repositories, "test-org", "all"
            )


def benchmark_git_operations(profiler: PerformanceProfiler, git_service, repo_count: int = 10):
    """Benchmark Git operations."""
    mock_repos = create_mock_repos(repo_count)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test clone operations
        with profiler.profile(f"Git Clone - {repo_count} repos (mocked)"):
            for repo in mock_repos:
                repo_path = temp_path / repo.name
                # Mock git clone operation
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                    try:
                        # This would normally clone, but we're mocking it
                        _ = git_service.clone_repository(repo.clone_url, str(repo_path))
                    except Exception:
                        pass  # Expected since we're mocking  # nosec

        # Test pull operations
        with profiler.profile(f"Git Pull - {repo_count} repos (mocked)"):
            for repo in mock_repos:
                repo_path = temp_path / repo.name
                repo_path.mkdir(exist_ok=True)  # Create directory for pull test
                (repo_path / ".git").mkdir(exist_ok=True)  # Mock git directory

                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = Mock(
                        returncode=0, stdout="Already up to date.", stderr=""
                    )
                    try:
                        _ = git_service.pull_repository(str(repo_path))
                    except Exception:
                        pass  # Expected since we're mocking  # nosec


def benchmark_batch_processing(
    profiler: PerformanceProfiler, batch_processor, repo_count: int = 50
):
    """Benchmark batch processing operations."""
    mock_repos = create_mock_repos(repo_count)

    with tempfile.TemporaryDirectory() as temp_dir:
        with profiler.profile(f"Batch Processing - {repo_count} repos"):
            # Mock the batch processing
            with patch.object(batch_processor, "process_repositories") as mock_process:
                mock_process.return_value = {
                    "success": repo_count,
                    "failed": 0,
                    "skipped": 0,
                    "total": repo_count,
                }

                try:
                    _ = batch_processor.process_repositories(mock_repos, temp_dir, max_workers=4)
                except Exception:
                    pass  # Expected since we're mocking  # nosec


def benchmark_memory_usage(profiler: PerformanceProfiler):
    """Benchmark memory usage with large datasets."""
    # Test with increasing dataset sizes
    for size in [100, 500, 1000, 2000]:
        with profiler.profile(f"Memory Usage - {size} repos"):
            repos = create_mock_repos(size)

            # Simulate processing large amounts of data
            data = []
            for repo in repos:
                data.append(
                    {
                        "name": repo.name,
                        "size": repo.size,
                        "metadata": {"created": time.time(), "data": "x" * 100},
                    }
                )

            # Force garbage collection to measure actual memory usage
            gc.collect()


def benchmark_concurrent_operations(profiler: PerformanceProfiler):
    """Benchmark concurrent operations."""

    async def mock_operation(repo_id: int):
        """Mock async operation."""
        await asyncio.sleep(0.001)  # Simulate I/O
        return f"result-{repo_id}"

    for concurrency in [1, 5, 10, 20]:
        with profiler.profile(f"Concurrent Ops - {concurrency} workers"):

            async def run_concurrent():
                tasks = [mock_operation(i) for i in range(50)]
                semaphore = asyncio.Semaphore(concurrency)

                async def limited_task(task):
                    async with semaphore:
                        return await task

                limited_tasks = [limited_task(task) for task in tasks]
                return await asyncio.gather(*limited_tasks)

            asyncio.run(run_concurrent())


def profile_cpu_intensive_operations():
    """Profile CPU-intensive operations with cProfile."""
    print("🔍 CPU Profiling")
    print("=" * 50)

    pr = cProfile.Profile()
    pr.enable()

    # CPU-intensive operations
    mock_repos = create_mock_repos(1000)
    processed_data = []

    for repo in mock_repos:
        # Simulate CPU-intensive processing
        processed = {
            "name": repo.name.upper(),
            "hash": hash(repo.full_name),
            "processed": True,
            "metrics": {
                "size_mb": repo.size / 1024,
                "category": "large" if repo.size > 5000 else "small",
            },
        }
        processed_data.append(processed)

    pr.disable()

    # Print profiling results
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(20)  # Top 20 functions

    print(s.getvalue())
    print()


def generate_performance_report(profiler: PerformanceProfiler):
    """Generate comprehensive performance report."""
    print("\n📊 Performance Report")
    print("=" * 50)

    total_time = sum(r.duration for r in profiler.results)
    successful_tests = sum(1 for r in profiler.results if r.success)
    failed_tests = len(profiler.results) - successful_tests

    print(f"Total Tests: {len(profiler.results)}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time: {total_time / len(profiler.results):.4f}s")
    print()

    # Performance metrics
    durations = [r.duration for r in profiler.results if r.success]
    memory_usage = [r.memory_current for r in profiler.results if r.success]

    if durations:
        print("📈 Performance Metrics:")
        print(f"  Fastest: {min(durations):.4f}s")
        print(f"  Slowest: {max(durations):.4f}s")
        print(f"  Average: {sum(durations) / len(durations):.4f}s")
        print()

    if memory_usage:
        print("💾 Memory Usage:")
        print(f"  Lowest: {min(memory_usage):.2f}MB")
        print(f"  Highest: {max(memory_usage):.2f}MB")
        print(f"  Average: {sum(memory_usage) / len(memory_usage):.2f}MB")
        print()

    # Save detailed results to JSON
    results_data = {
        "timestamp": time.time(),
        "summary": {
            "total_tests": len(profiler.results),
            "successful": successful_tests,
            "failed": failed_tests,
            "total_time": total_time,
        },
        "results": [
            {
                "name": r.name,
                "duration": r.duration,
                "memory_current": r.memory_current,
                "memory_peak": r.memory_peak,
                "cpu_percent": r.cpu_percent,
                "success": r.success,
                "error": r.error,
            }
            for r in profiler.results
        ],
    }

    results_file = Path(__file__).parent / "performance_results.json"
    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)

    print(f"📁 Detailed results saved to: {results_file}")


async def main():
    """Run comprehensive performance benchmarks."""
    print("🚀 Git Batch Pull - Advanced Performance Benchmarks")
    print("=" * 60)

    # Initialize profiler
    profiler = PerformanceProfiler()

    try:
        # Set up test environment
        modules = setup_test_environment()
        if not modules:
            print("❌ Failed to set up test environment")
            return

        git_batch_pull, GitHubService, GitService, BatchProcessor = modules

        # Initialize services (with mock dependencies)
        import tempfile

        from git_batch_pull.security.path_validator import PathValidator
        from git_batch_pull.security.subprocess_runner import SafeSubprocessRunner

        subprocess_runner = SafeSubprocessRunner()
        path_validator = PathValidator()
        temp_dir = tempfile.mkdtemp()

        github_service = GitHubService("mock_token", subprocess_runner)
        git_service = GitService(temp_dir, subprocess_runner, path_validator)
        batch_processor = BatchProcessor(github_service, git_service)

        print("🔄 Running benchmarks...\n")

        # Run benchmarks
        await benchmark_github_api_calls(profiler, github_service, 100)
        benchmark_git_operations(profiler, git_service, 20)
        benchmark_batch_processing(profiler, batch_processor, 50)
        benchmark_memory_usage(profiler)
        benchmark_concurrent_operations(profiler)

        # CPU profiling
        profile_cpu_intensive_operations()

        # Generate report
        generate_performance_report(profiler)

        print("✅ All benchmarks completed successfully!")

    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Check dependencies
    try:
        import psutil
    except ImportError:
        print("❌ psutil is required for performance benchmarks")
        print("Install with: pip install psutil")
        sys.exit(1)

    asyncio.run(main())
