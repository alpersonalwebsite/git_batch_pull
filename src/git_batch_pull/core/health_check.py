"""
Health check system for git-batch-pull.

Provides system health monitoring and diagnostics.
"""

import asyncio
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from ..models.config import Config


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: str  # "ok", "warning", "error"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """System health checker."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def run_all_checks(self) -> List[HealthCheckResult]:
        """Run all health checks."""
        checks = [
            self._check_python_version(),
            self._check_git_installation(),
            self._check_network_connectivity(),
            self._check_github_api_access(),
            self._check_disk_space(),
            self._check_permissions(),
        ]

        if self.config:
            checks.append(self._check_local_folder())

        # Run checks concurrently where possible
        results = []
        for check in checks:
            try:
                if asyncio.iscoroutine(check):
                    result = await check
                else:
                    result = check
                results.append(result)
            except Exception as e:
                results.append(
                    HealthCheckResult(
                        name="unknown", status="error", message=f"Health check failed: {e}"
                    )
                )

        return results

    def _check_python_version(self) -> HealthCheckResult:
        """Check Python version compatibility."""
        version = sys.version_info
        min_version = (3, 8)

        if version >= min_version:
            return HealthCheckResult(
                name="python_version",
                status="ok",
                message=f"Python {version.major}.{version.minor}.{version.micro}",
                details={"version": sys.version},
            )
        else:
            return HealthCheckResult(
                name="python_version",
                status="error",
                message=(
                    f"Python {version.major}.{version.minor} is not supported. "
                    f"Minimum required: {min_version[0]}.{min_version[1]}"
                ),
                details={"version": sys.version, "minimum": f"{min_version[0]}.{min_version[1]}"},
            )

    def _check_git_installation(self) -> HealthCheckResult:
        """Check Git installation and version."""
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, check=True
            )
            version = result.stdout.strip()
            return HealthCheckResult(
                name="git_installation",
                status="ok",
                message=f"Git installed: {version}",
                details={"version": version, "executable": shutil.which("git")},
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return HealthCheckResult(
                name="git_installation",
                status="error",
                message=f"Git not available: {e}",
                details={"error": str(e)},
            )

    async def _check_network_connectivity(self) -> HealthCheckResult:
        """Check basic network connectivity."""
        try:
            response = requests.get("https://httpbin.org/get", timeout=5)
            if response.status_code == 200:
                return HealthCheckResult(
                    name="network_connectivity",
                    status="ok",
                    message="Network connectivity available",
                )
            else:
                return HealthCheckResult(
                    name="network_connectivity",
                    status="warning",
                    message=f"Network test returned status {response.status_code}",
                )
        except Exception as e:
            return HealthCheckResult(
                name="network_connectivity",
                status="error",
                message=f"Network connectivity failed: {e}",
                details={"error": str(e)},
            )

    async def _check_github_api_access(self) -> HealthCheckResult:
        """Check GitHub API accessibility."""
        try:
            response = requests.get("https://api.github.com/rate_limit", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return HealthCheckResult(
                    name="github_api_access",
                    status="ok",
                    message="GitHub API accessible",
                    details={
                        "rate_limit": data.get("rate", {}),
                        "core_remaining": data.get("rate", {}).get("remaining", 0),
                    },
                )
            else:
                return HealthCheckResult(
                    name="github_api_access",
                    status="warning",
                    message=f"GitHub API returned status {response.status_code}",
                    details={"status_code": response.status_code},
                )
        except Exception as e:
            return HealthCheckResult(
                name="github_api_access",
                status="error",
                message=f"GitHub API access failed: {e}",
                details={"error": str(e)},
            )

    def _check_disk_space(self) -> HealthCheckResult:
        """Check available disk space."""
        try:
            # Check space in home directory
            home = Path.home()
            stat = shutil.disk_usage(home)

            # Convert to GB
            free_gb = stat.free / (1024**3)
            total_gb = stat.total / (1024**3)

            if free_gb > 1.0:  # At least 1GB free
                status = "ok"
                message = f"Sufficient disk space: {free_gb:.1f}GB free of {total_gb:.1f}GB"
            elif free_gb > 0.1:  # At least 100MB free
                status = "warning"
                message = f"Low disk space: {free_gb:.1f}GB free of {total_gb:.1f}GB"
            else:
                status = "error"
                message = f"Critical disk space: {free_gb:.1f}GB free of {total_gb:.1f}GB"

            return HealthCheckResult(
                name="disk_space",
                status=status,
                message=message,
                details={
                    "free_bytes": stat.free,
                    "total_bytes": stat.total,
                    "used_bytes": stat.used,
                },
            )
        except Exception as e:
            return HealthCheckResult(
                name="disk_space",
                status="error",
                message=f"Cannot check disk space: {e}",
                details={"error": str(e)},
            )

    def _check_permissions(self) -> HealthCheckResult:
        """Check file system permissions."""
        try:
            # Check write permissions in home directory
            home = Path.home()
            test_file = home / ".git_batch_pull_test"

            # Try to create and delete a test file
            test_file.write_text("test")
            test_file.unlink()

            return HealthCheckResult(
                name="permissions", status="ok", message="File system permissions OK"
            )
        except Exception as e:
            return HealthCheckResult(
                name="permissions",
                status="error",
                message=f"Permission error: {e}",
                details={"error": str(e)},
            )

    def _check_local_folder(self) -> HealthCheckResult:
        """Check local folder configuration."""
        if not self.config or not self.config.local_folder:
            return HealthCheckResult(
                name="local_folder", status="warning", message="No local folder configured"
            )

        try:
            folder = Path(self.config.local_folder)
            if not folder.exists():
                return HealthCheckResult(
                    name="local_folder",
                    status="warning",
                    message=f"Local folder does not exist: {folder}",
                    details={"path": str(folder)},
                )

            if not folder.is_dir():
                return HealthCheckResult(
                    name="local_folder",
                    status="error",
                    message=f"Local folder path is not a directory: {folder}",
                    details={"path": str(folder)},
                )

            # Check if writable
            test_file = folder / ".git_batch_pull_test"
            test_file.write_text("test")
            test_file.unlink()

            return HealthCheckResult(
                name="local_folder",
                status="ok",
                message=f"Local folder accessible: {folder}",
                details={"path": str(folder)},
            )
        except Exception as e:
            return HealthCheckResult(
                name="local_folder",
                status="error",
                message=f"Local folder check failed: {e}",
                details={"error": str(e), "path": str(self.config.local_folder)},
            )


def format_health_report(results: List[HealthCheckResult]) -> str:
    """Format health check results into a readable report."""
    lines = ["🏥 Git Batch Pull Health Check", "=" * 40]

    status_counts = {"ok": 0, "warning": 0, "error": 0}

    for result in results:
        status_counts[result.status] += 1

        # Status icon
        if result.status == "ok":
            icon = "✅"
        elif result.status == "warning":
            icon = "⚠️"
        else:
            icon = "❌"

        lines.append(f"{icon} {result.name}: {result.message}")

        # Add details if available and status is not ok
        if result.details and result.status != "ok":
            for key, value in result.details.items():
                lines.append(f"   {key}: {value}")

    # Summary
    lines.extend(
        [
            "",
            "Summary:",
            f"  ✅ OK: {status_counts['ok']}",
            f"  ⚠️  Warnings: {status_counts['warning']}",
            f"  ❌ Errors: {status_counts['error']}",
        ]
    )

    # Overall status
    if status_counts["error"] > 0:
        lines.append("\n🔴 Overall Status: ISSUES DETECTED")
    elif status_counts["warning"] > 0:
        lines.append("\n🟡 Overall Status: WARNINGS PRESENT")
    else:
        lines.append("\n🟢 Overall Status: ALL SYSTEMS GO")

    return "\n".join(lines)
