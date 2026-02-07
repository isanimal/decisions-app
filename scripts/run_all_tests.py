#!/usr/bin/env python3
"""
Master Test Runner - Orchestrates all QA test suites
Runs: smoke tests, comprehensive tests, and security tests
Generates consolidated report
Usage: python run_all_tests.py [--url http://localhost:8000] [--suite smoke|comprehensive|security|all]
"""

import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000"

class TestRunner:
    """Orchestrates all test suites"""
    
    def __init__(self, base_url: str = BASE_URL, verbose: bool = False):
        self.base_url = base_url
        self.verbose = verbose
        self.results = {}
        self.start_time = datetime.now()
    
    def run_suite(self, script_name: str, suite_name: str) -> bool:
        """Run a test suite script"""
        print(f"\n{'='*80}")
        print(f"Running {suite_name}...".center(80))
        print(f"{'='*80}\n")
        
        script_path = SCRIPTS_DIR / script_name
        
        if not script_path.exists():
            print(f"✗ Script not found: {script_path}")
            return False
        
        cmd = [
            sys.executable,
            str(script_path),
            "--url", self.base_url
        ]
        
        if self.verbose:
            cmd.append("--verbose")
        
        try:
            result = subprocess.run(
                cmd,
                timeout=300,
                capture_output=False
            )
            
            self.results[suite_name] = {
                "exit_code": result.returncode,
                "passed": result.returncode == 0,
                "timestamp": datetime.now().isoformat()
            }
            
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"\n✗ {suite_name} timed out")
            self.results[suite_name] = {
                "exit_code": -1,
                "passed": False,
                "error": "Timeout"
            }
            return False
        except Exception as e:
            print(f"\n✗ Error running {suite_name}: {e}")
            self.results[suite_name] = {
                "exit_code": -1,
                "passed": False,
                "error": str(e)
            }
            return False
    
    def run_all_suites(self):
        """Run all test suites in sequence"""
        print("\n" + "="*80)
        print("SECURE DECISION APP - MASTER TEST SUITE".center(80))
        print(f"Target: {self.base_url}".center(80))
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}".center(80))
        print("="*80)
        
        suites = [
            ("qa_smoke_test.py", "Smoke Tests"),
            ("qa_test_suite.py", "Comprehensive Tests"),
            ("qa_security_tests.py", "Security Tests")
        ]
        
        passed_count = 0
        for script, name in suites:
            if self.run_suite(script, name):
                passed_count += 1
            time.sleep(1)  # Brief pause between suites
        
        return self.print_summary(passed_count, len(suites))
    
    def print_summary(self, passed: int, total: int) -> bool:
        """Print consolidated summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*80)
        print("MASTER TEST SUMMARY".center(80))
        print("="*80)
        print(f"Total Suites:      {total}")
        print(f"Passed:            {passed} ✓")
        print(f"Failed:            {total - passed} ✗")
        print(f"Success Rate:      {(passed/total)*100:.1f}%")
        print(f"Total Duration:    {duration:.1f} seconds")
        print("="*80)
        
        print("\nSuite Results:")
        print("-"*80)
        for suite_name, result in self.results.items():
            status = "✓ PASS" if result.get("passed") else "✗ FAIL"
            error = f" ({result.get('error')})" if "error" in result else ""
            print(f"{suite_name:30s} {status}{error}")
        
        print("\n" + "="*80)
        if passed == total:
            print("✓ ALL TEST SUITES PASSED".center(80))
            print("Application is ready for deployment".center(80))
        else:
            print("✗ SOME TEST SUITES FAILED".center(80))
            print("Fix failures before deployment".center(80))
        print("="*80 + "\n")
        
        return passed == total


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Master Test Runner - Orchestrates all QA suites"
    )
    parser.add_argument(
        "--url",
        default=BASE_URL,
        help=f"Base URL (default: {BASE_URL})"
    )
    parser.add_argument(
        "--suite",
        choices=["smoke", "comprehensive", "security", "all"],
        default="all",
        help="Which test suite to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(base_url=args.url, verbose=args.verbose)
    
    if args.suite == "all":
        success = runner.run_all_suites()
    else:
        suites_map = {
            "smoke": ("qa_smoke_test.py", "Smoke Tests"),
            "comprehensive": ("qa_test_suite.py", "Comprehensive Tests"),
            "security": ("qa_security_tests.py", "Security Tests")
        }
        script, name = suites_map[args.suite]
        success = runner.run_suite(script, name)
        print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
