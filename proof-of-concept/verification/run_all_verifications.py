#!/usr/bin/env python3
"""Master verification test runner.

Executes all verification suites and generates comprehensive reports:
- Console summary (pass/fail counts)
- JSON report (for CI integration)
- HTML report (human-readable)
- Exit code (0 = all pass, 1 = failures)

Usage:
    python run_all_verifications.py
    python run_all_verifications.py --verbose
    python run_all_verifications.py --html-report report.html
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class TestResult:
    """Container for test results."""

    def __init__(self, module: str):
        """Initialize test result."""
        self.module = module
        self.passed = 0
        self.failed = 0
        self.errors = 0
        self.skipped = 0
        self.duration = 0.0
        self.output = ""


class VerificationRunner:
    """Master verification test runner."""

    def __init__(self, verbose: bool = False):
        """Initialize runner.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.start_time = datetime.now()

    def run_test_module(self, module_path: Path) -> TestResult:
        """Run a single test module.

        Args:
            module_path: Path to test module

        Returns:
            TestResult with execution results
        """
        result = TestResult(module_path.name)

        print(f"\n{'='*60}")
        print(f"Running: {module_path.name}")
        print(f"{'='*60}")

        # Run pytest on this module
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(module_path),
            "-v" if self.verbose else "-q",
            "--tb=short",
            "--color=yes",
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per module
            )

            result.output = proc.stdout + proc.stderr

            # Parse pytest output for counts
            # This is a simple parse - pytest-json-report would be better for production
            output = result.output.lower()

            # Look for summary line like "5 passed, 2 failed"
            if "passed" in output:
                for line in output.split("\n"):
                    if "passed" in line:
                        import re

                        # Match patterns like "5 passed" or "5 passed, 2 failed"
                        passed_match = re.search(r"(\d+)\s+passed", line)
                        failed_match = re.search(r"(\d+)\s+failed", line)
                        error_match = re.search(r"(\d+)\s+error", line)
                        skip_match = re.search(r"(\d+)\s+skipped", line)

                        if passed_match:
                            result.passed = int(passed_match.group(1))
                        if failed_match:
                            result.failed = int(failed_match.group(1))
                        if error_match:
                            result.errors = int(error_match.group(1))
                        if skip_match:
                            result.skipped = int(skip_match.group(1))

            # Print output
            print(result.output)

            if proc.returncode == 0:
                print(f"✅ {module_path.name}: PASSED")
            else:
                print(f"❌ {module_path.name}: FAILED")

        except subprocess.TimeoutExpired:
            print(f"⏱️  {module_path.name}: TIMEOUT")
            result.errors = 1
        except Exception as e:
            print(f"💥 {module_path.name}: ERROR - {e}")
            result.errors = 1

        return result

    def run_all_tests(self) -> bool:
        """Run all verification test modules.

        Returns:
            True if all tests passed, False otherwise
        """
        # Find all test modules
        test_dir = Path(__file__).parent
        test_modules = sorted(test_dir.glob("test_*.py"))

        if not test_modules:
            print("❌ No test modules found!")
            return False

        print(f"\n{'='*60}")
        print(f"VERIFICATION TEST SUITE")
        print(f"{'='*60}")
        print(f"Found {len(test_modules)} test modules")
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Run each test module
        for module_path in test_modules:
            result = self.run_test_module(module_path)
            self.results.append(result)

        return all(
            r.failed == 0 and r.errors == 0 for r in self.results
        )

    def generate_console_report(self) -> None:
        """Generate console summary report."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print(f"\n{'='*60}")
        print("VERIFICATION TEST SUMMARY")
        print(f"{'='*60}")

        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_skipped = sum(r.skipped for r in self.results)

        for result in self.results:
            status = "✅ PASS" if result.failed == 0 and result.errors == 0 else "❌ FAIL"
            print(
                f"{status} | {result.module:40s} | "
                f"P:{result.passed:3d} F:{result.failed:3d} E:{result.errors:3d} S:{result.skipped:3d}"
            )

        print(f"{'='*60}")
        print(f"Total:   Passed: {total_passed:3d} | Failed: {total_failed:3d} | "
              f"Errors: {total_errors:3d} | Skipped: {total_skipped:3d}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        if total_failed == 0 and total_errors == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n❌ {total_failed + total_errors} TESTS FAILED")

    def generate_json_report(self, output_path: Path) -> None:
        """Generate JSON report for CI integration.

        Args:
            output_path: Path to write JSON report
        """
        report = {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "modules": [
                {
                    "name": r.module,
                    "passed": r.passed,
                    "failed": r.failed,
                    "errors": r.errors,
                    "skipped": r.skipped,
                }
                for r in self.results
            ],
            "summary": {
                "total_passed": sum(r.passed for r in self.results),
                "total_failed": sum(r.failed for r in self.results),
                "total_errors": sum(r.errors for r in self.results),
                "total_skipped": sum(r.skipped for r in self.results),
                "all_passed": all(r.failed == 0 and r.errors == 0 for r in self.results),
            },
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 JSON report written to: {output_path}")

    def generate_html_report(self, output_path: Path) -> None:
        """Generate HTML report for human review.

        Args:
            output_path: Path to write HTML report
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Verification Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .pass {{ background-color: #d4edda; }}
        .fail {{ background-color: #f8d7da; }}
        .summary {{ background-color: #f0f0f0; padding: 15px; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Verification Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Start Time:</strong> {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Duration:</strong> {(datetime.now() - self.start_time).total_seconds():.2f} seconds</p>
        <p><strong>Total Passed:</strong> {sum(r.passed for r in self.results)}</p>
        <p><strong>Total Failed:</strong> {sum(r.failed for r in self.results)}</p>
        <p><strong>Total Errors:</strong> {sum(r.errors for r in self.results)}</p>
        <p><strong>Total Skipped:</strong> {sum(r.skipped for r in self.results)}</p>
    </div>

    <h2>Test Modules</h2>
    <table>
        <tr>
            <th>Module</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Errors</th>
            <th>Skipped</th>
            <th>Status</th>
        </tr>
"""

        for result in self.results:
            status = "PASS" if result.failed == 0 and result.errors == 0 else "FAIL"
            row_class = "pass" if status == "PASS" else "fail"

            html += f"""        <tr class="{row_class}">
            <td>{result.module}</td>
            <td>{result.passed}</td>
            <td>{result.failed}</td>
            <td>{result.errors}</td>
            <td>{result.skipped}</td>
            <td>{status}</td>
        </tr>
"""

        html += """    </table>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html)

        print(f"📄 HTML report written to: {output_path}")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Run all verification tests and generate reports"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        default=Path("verification-report.json"),
        help="Path for JSON report (default: verification-report.json)",
    )
    parser.add_argument(
        "--html-report",
        type=Path,
        default=Path("verification-report.html"),
        help="Path for HTML report (default: verification-report.html)",
    )
    args = parser.parse_args()

    # Run all tests
    runner = VerificationRunner(verbose=args.verbose)
    all_passed = runner.run_all_tests()

    # Generate reports
    runner.generate_console_report()
    runner.generate_json_report(args.json_report)
    runner.generate_html_report(args.html_report)

    # Exit with appropriate code
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
