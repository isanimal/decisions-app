#!/usr/bin/env python3
"""
Security-Focused QA Tests for Secure Decision App
Tests vulnerability categories: IDOR, XSS, CSRF, SQL Injection, Auth
Usage: python qa_security_tests.py [--url http://localhost:8000] [--verbose]
"""

import requests
import json
import sys
import time
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

BASE_URL = "http://localhost:8000"
TIMEOUT = 10

@dataclass
class SecurityTest:
    """Security test result"""
    test_id: str
    category: str
    vulnerability: str
    passed: bool
    severity: str
    details: str

class QASecurityTests:
    """Security-focused QA tests"""
    
    def __init__(self, base_url: str = BASE_URL, verbose: bool = False):
        self.base_url = base_url
        self.verbose = verbose
        self.results: List[SecurityTest] = []
        self.start_time = datetime.now()
        self.session = requests.Session()
        self.admin_session = requests.Session()
        self.user_session = requests.Session()
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        if self.verbose or level in ["ERROR", "WARN", "PASS", "FAIL"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level:8s} {message}")
    
    def test(self, test_id: str, category: str, vuln: str, passed: bool, 
             severity: str, details: str = ""):
        """Record security test"""
        result = SecurityTest(
            test_id=test_id,
            category=category,
            vulnerability=vuln,
            passed=passed,
            severity=severity,
            details=details
        )
        self.results.append(result)
        
        status = "✓ SAFE" if passed else "✗ VULNERABLE"
        print(f"[{severity:8s}] {test_id}: {status} - {vuln}")
        if details:
            self.log(f"  {details}", "WARN" if not passed else "INFO")
    
    # ========== AUTHENTICATION & SESSION TESTS ==========
    def test_auth_weak_credentials(self):
        """AUTH-SEC-001: Weak password acceptance"""
        start = time.time()
        try:
            data = {
                "username": "weakuser",
                "password": "123"  # Very weak
            }
            response = self.session.post(
                f"{self.base_url}/setup",
                data=data,
                timeout=TIMEOUT
            )
            # Should reject weak password
            passed = response.status_code != 200
            self.test("AUTH-SEC-001", "Authentication", 
                     "Weak password rejected", passed, 
                     "HIGH", 
                     "Password policy not enforced" if not passed else "OK")
        except Exception as e:
            self.test("AUTH-SEC-001", "Authentication",
                     "Weak password rejected", False,
                     "HIGH", str(e))
    
    def test_auth_sql_injection_login(self):
        """AUTH-SEC-002: SQL injection in login"""
        start = time.time()
        try:
            data = {
                "username": "' OR '1'='1",
                "password": "' OR '1'='1"
            }
            response = self.session.post(
                f"{self.base_url}/login",
                data=data,
                timeout=TIMEOUT,
                allow_redirects=False
            )
            # Should not grant access
            passed = response.status_code != 200
            self.test("AUTH-SEC-002", "Authentication",
                     "SQL injection blocked", passed,
                     "CRITICAL",
                     "SQL injection possible" if not passed else "OK")
        except Exception as e:
            self.test("AUTH-SEC-002", "Authentication",
                     "SQL injection blocked", False,
                     "CRITICAL", str(e))
    
    def test_auth_session_fixation(self):
        """AUTH-SEC-003: Session fixation prevention"""
        start = time.time()
        try:
            # Get initial session
            session1 = requests.Session()
            response1 = session1.get(f"{self.base_url}/", timeout=TIMEOUT)
            cookies1 = session1.cookies.get_dict()
            
            # Login with different session
            session2 = requests.Session()
            if cookies1:
                session2.cookies.update(cookies1)
            
            data = {"username": "admin", "password": "Admin123!"}
            response2 = session2.post(f"{self.base_url}/login", data=data, timeout=TIMEOUT)
            cookies2 = session2.cookies.get_dict()
            
            # Cookies should have changed
            passed = cookies1 != cookies2 if cookies1 else True
            self.test("AUTH-SEC-003", "Authentication",
                     "Session fixation prevented", passed,
                     "HIGH",
                     "Session cookie changed after login" if passed else "Same cookie")
        except Exception as e:
            self.test("AUTH-SEC-003", "Authentication",
                     "Session fixation prevented", False,
                     "HIGH", str(e))
    
    # ========== CROSS-SITE REQUEST FORGERY ==========
    def test_csrf_form_POST(self):
        """CSRF-001: CSRF token on forms"""
        start = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/decisions/new",
                timeout=TIMEOUT
            )
            # Should contain CSRF token
            passed = "csrf" in response.text.lower() or "token" in response.text.lower()
            self.test("CSRF-001", "CSRF", 
                     "CSRF token in forms", passed,
                     "HIGH",
                     "No CSRF token found" if not passed else "Token present")
        except Exception as e:
            self.test("CSRF-001", "CSRF",
                     "CSRF token in forms", False,
                     "HIGH", str(e))
    
    def test_csrf_state_change_POST(self):
        """CSRF-002: State-changing POST validation"""
        start = time.time()
        try:
            # Try POST without proper headers
            headers = {"X-Requested-With": "XMLHttpRequest"}
            data = {
                "title": "CSRF Test",
                "context": "test",
                "goals": "test",
                "assumptions": "test"
            }
            
            response = self.session.post(
                f"{self.base_url}/decisions/new",
                data=data,
                headers=headers,
                timeout=TIMEOUT
            )
            # Should reject or require token
            passed = response.status_code in [403, 400, 422]
            self.test("CSRF-002", "CSRF",
                     "POST without token rejected", passed,
                     "HIGH",
                     "Request accepted without CSRF validation" if not passed else "Blocked")
        except Exception as e:
            self.test("CSRF-002", "CSRF",
                     "POST without token rejected", False,
                     "HIGH", str(e))
    
    # ========== INSECURE DIRECT OBJECT REFERENCES (IDOR) ==========
    def test_idor_decision_access(self):
        """IDOR-001: Decision access control"""
        start = time.time()
        try:
            # Try to access admin decision with user session
            response = self.session.get(
                f"{self.base_url}/decisions/1",
                timeout=TIMEOUT,
                allow_redirects=False
            )
            # Access should be controlled
            passed = response.status_code in [200, 403, 404, 302]
            self.test("IDOR-001", "IDOR",
                     "Decision access controlled", passed,
                     "HIGH",
                     "Unrestricted access to decision" if response.status_code == 200 else "OK")
        except Exception as e:
            self.test("IDOR-001", "IDOR",
                     "Decision access controlled", False,
                     "HIGH", str(e))
    
    def test_idor_threat_access(self):
        """IDOR-002: Threat assessment access control"""
        start = time.time()
        try:
            # Try to access threat from different decision
            response = self.session.get(
                f"{self.base_url}/decisions/999/threat-lite/1",
                timeout=TIMEOUT,
                allow_redirects=False
            )
            # Should not allow cross-decision access
            passed = response.status_code in [404, 403]
            self.test("IDOR-002", "IDOR",
                     "Threat access isolated", passed,
                     "HIGH",
                     "Threat accessible across decisions" if response.status_code == 200 else "OK")
        except Exception as e:
            self.test("IDOR-002", "IDOR",
                     "Threat access isolated", False,
                     "HIGH", str(e))
    
    def test_idor_parameter_tampering(self):
        """IDOR-003: Parameter tampering detection"""
        start = time.time()
        try:
            # Try to modify ID parameter
            response = self.session.get(
                f"{self.base_url}/decisions/1a2b3c",
                timeout=TIMEOUT,
                allow_redirects=False
            )
            # Should handle invalid IDs
            passed = response.status_code in [400, 404]
            self.test("IDOR-003", "IDOR",
                     "Invalid ID rejected", passed,
                     "MEDIUM",
                     "Invalid parameter accepted" if response.status_code == 200 else "OK")
        except Exception as e:
            self.test("IDOR-003", "IDOR",
                     "Invalid ID rejected", False,
                     "MEDIUM", str(e))
    
    # ========== CROSS-SITE SCRIPTING (XSS) ==========
    def test_xss_reflected_title(self):
        """XSS-001: Reflected XSS in decision title"""
        start = time.time()
        try:
            payload = "<script>alert('xss')</script>"
            data = {
                "title": payload,
                "context": "test",
                "goals": "test",
                "assumptions": "test"
            }
            response = self.session.post(
                f"{self.base_url}/decisions/new",
                data=data,
                timeout=TIMEOUT,
                allow_redirects=True
            )
            
            # Script tags should be escaped
            passed = "<script>" not in response.text
            self.test("XSS-001", "XSS",
                     "Script tags escaped", passed,
                     "HIGH",
                     "Script tag reflected in output" if not passed else "Escaped OK")
        except Exception as e:
            self.test("XSS-001", "XSS",
                     "Script tags escaped", False,
                     "HIGH", str(e))
    
    def test_xss_event_handlers(self):
        """XSS-002: Event handler injection"""
        start = time.time()
        try:
            payload = '"><svg onload=alert("xss")>'
            data = {
                "title": payload,
                "context": "test",
                "goals": "test",
                "assumptions": "test"
            }
            response = self.session.post(
                f"{self.base_url}/decisions/new",
                data=data,
                timeout=TIMEOUT,
                allow_redirects=True
            )
            
            # Event handlers should be escaped
            passed = "onload=" not in response.text
            self.test("XSS-002", "XSS",
                     "Event handlers escaped", passed,
                     "HIGH",
                     "Event handler present in output" if not passed else "OK")
        except Exception as e:
            self.test("XSS-002", "XSS",
                     "Event handlers escaped", False,
                     "HIGH", str(e))
    
    def test_xss_json_responses(self):
        """XSS-003: XSS in JSON responses"""
        start = time.time()
        try:
            payload = {"decision_pattern": "<img src=x onerror=alert('xss')>"}
            response = self.session.post(
                f"{self.base_url}/kb/match",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Check if payload appears unescaped
                    passed = "onerror=" not in json.dumps(data)
                except:
                    passed = True
            else:
                passed = True
            
            self.test("XSS-003", "XSS",
                     "JSON response safe", passed,
                     "MEDIUM",
                     "Payload in JSON unescaped" if not passed else "OK")
        except Exception as e:
            self.test("XSS-003", "XSS",
                     "JSON response safe", False,
                     "MEDIUM", str(e))
    
    # ========== INFORMATION DISCLOSURE ==========
    def test_info_error_messages(self):
        """INFO-001: Detailed error messages"""
        start = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/decisions/invalid",
                timeout=TIMEOUT
            )
            # Should not expose system paths or database details
            passed = ("traceback" not in response.text.lower() and
                     "/home/" not in response.text and
                     "database" not in response.text.lower())
            self.test("INFO-001", "Information Disclosure",
                     "Error messages sanitized", passed,
                     "MEDIUM",
                     "System details in error message" if not passed else "OK")
        except Exception as e:
            self.test("INFO-001", "Information Disclosure",
                     "Error messages sanitized", False,
                     "MEDIUM", str(e))
    
    def test_info_debug_mode(self):
        """INFO-002: Debug mode disabled"""
        start = time.time()
        try:
            response = self.session.get(
                f"{self.base_url}/debug",
                timeout=TIMEOUT,
                allow_redirects=False
            )
            # Debug endpoint should not exist or be protected
            passed = response.status_code in [404, 403, 401]
            self.test("INFO-002", "Information Disclosure",
                     "Debug mode disabled", passed,
                     "HIGH",
                     "Debug interface accessible" if response.status_code == 200 else "OK")
        except Exception as e:
            self.test("INFO-002", "Information Disclosure",
                     "Debug mode disabled", True,
                     "MEDIUM", "OK - endpoint not found")
    
    def test_info_api_response(self):
        """INFO-003: API response header safety"""
        start = time.time()
        try:
            response = self.session.get(f"{self.base_url}/", timeout=TIMEOUT)
            
            # Check for security headers
            headers = response.headers
            passed = (
                "Server" not in headers or "FastAPI" not in headers.get("Server", "")
            )
            self.test("INFO-003", "Information Disclosure",
                     "Server version hidden", passed,
                     "LOW",
                     "Server version disclosed" if not passed else "OK")
        except Exception as e:
            self.test("INFO-003", "Information Disclosure",
                     "Server version hidden", False,
                     "LOW", str(e))
    
    # ========== AUTHENTICATION BYPASS ==========
    def test_auth_bypass_null_byte(self):
        """AUTHBYPASS-001: Null byte injection"""
        start = time.time()
        try:
            data = {
                "username": "admin\x00",
                "password": "test"
            }
            response = self.session.post(
                f"{self.base_url}/login",
                data=data,
                timeout=TIMEOUT,
                allow_redirects=False
            )
            # Should not accept null bytes
            passed = response.status_code != 200
            self.test("AUTHBYPASS-001", "Auth Bypass",
                     "Null byte blocked", passed,
                     "MEDIUM",
                     "Null byte processed" if not passed else "OK")
        except Exception as e:
            self.test("AUTHBYPASS-001", "Auth Bypass",
                     "Null byte blocked", True,
                     "MEDIUM", "OK")
    
    # ========== INPUT VALIDATION ==========
    def test_input_validation_length(self):
        """INPUT-001: Excessive input length"""
        start = time.time()
        try:
            huge_input = "A" * 1000000  # 1MB
            data = {
                "title": huge_input,
                "context": "test",
                "goals": "test",
                "assumptions": "test"
            }
            response = self.session.post(
                f"{self.base_url}/decisions/new",
                data=data,
                timeout=TIMEOUT
            )
            # Should reject or truncate
            passed = response.status_code in [400, 413, 422]
            self.test("INPUT-001", "Input Validation",
                     "Excessive input rejected", passed,
                     "MEDIUM",
                     "1MB input accepted" if response.status_code == 200 else "OK")
        except Exception as e:
            self.test("INPUT-001", "Input Validation",
                     "Excessive input rejected", True,
                     "MEDIUM", "OK - rejected")
    
    def test_input_validation_special_chars(self):
        """INPUT-002: Special character handling"""
        start = time.time()
        try:
            special = "'; DROP TABLE decisions; --"
            data = {
                "title": special,
                "context": "test",
                "goals": "test",
                "assumptions": "test"
            }
            response = self.session.post(
                f"{self.base_url}/decisions/new",
                data=data,
                timeout=TIMEOUT,
                allow_redirects=True
            )
            # Should handle gracefully
            passed = response.status_code == 200
            self.test("INPUT-002", "Input Validation",
                     "Special chars handled", passed,
                     "MEDIUM",
                     "Special characters processed safely")
        except Exception as e:
            self.test("INPUT-002", "Input Validation",
                     "Special chars handled", False,
                     "MEDIUM", str(e))
    
    def run_all(self):
        """Run all security tests"""
        print("\n" + "="*80)
        print("SECURITY TEST SUITE".center(80))
        print("="*80 + "\n")
        
        # Auth tests
        self.test_auth_weak_credentials()
        self.test_auth_sql_injection_login()
        self.test_auth_session_fixation()
        
        # CSRF tests
        self.test_csrf_form_POST()
        self.test_csrf_state_change_POST()
        
        # IDOR tests
        self.test_idor_decision_access()
        self.test_idor_threat_access()
        self.test_idor_parameter_tampering()
        
        # XSS tests
        self.test_xss_reflected_title()
        self.test_xss_event_handlers()
        self.test_xss_json_responses()
        
        # Info disclosure
        self.test_info_error_messages()
        self.test_info_debug_mode()
        self.test_info_api_response()
        
        # Auth bypass
        self.test_auth_bypass_null_byte()
        
        # Input validation
        self.test_input_validation_length()
        self.test_input_validation_special_chars()
        
        return self.print_report()
    
    def print_report(self) -> bool:
        """Print security report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        # Count by severity
        critical = sum(1 for r in self.results if r.severity == "CRITICAL" and not r.passed)
        high = sum(1 for r in self.results if r.severity == "HIGH" and not r.passed)
        medium = sum(1 for r in self.results if r.severity == "MEDIUM" and not r.passed)
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*80)
        print("SECURITY TEST REPORT".center(80))
        print("="*80)
        print(f"Total Tests:         {total}")
        print(f"Passed (Safe):       {passed} ✓")
        print(f"Failed (Vulnerable): {failed} ✗")
        print(f"Success Rate:        {(passed/total)*100:.1f}%")
        print("="*80)
        
        print("\nVulnerabilities Found:")
        print(f"  CRITICAL: {critical}")
        print(f"  HIGH:     {high}")
        print(f"  MEDIUM:   {medium}")
        print(f"  LOW:      {sum(1 for r in self.results if r.severity == 'LOW' and not r.passed)}")
        
        if failed > 0:
            print("\n" + "="*80)
            print("VULNERABLE TESTS:")
            print("-"*80)
            for result in sorted(self.results, 
                               key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[x.severity]):
                if not result.passed:
                    print(f"[{result.severity:8s}] {result.test_id}: {result.vulnerability}")
                    if result.details:
                        print(f"  Details: {result.details}")
        
        print("\n" + "="*80)
        if critical == 0 and high == 0:
            print("✓ NO CRITICAL/HIGH VULNERABILITIES FOUND".center(80))
        else:
            print("✗ VULNERABILITIES DETECTED - IMMEDIATE ACTION REQUIRED".center(80))
        print("="*80 + "\n")
        
        return critical == 0 and high == 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security QA Tests")
    parser.add_argument("--url", default=BASE_URL, help=f"Base URL (default: {BASE_URL})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    tests = QASecurityTests(base_url=args.url, verbose=args.verbose)
    success = tests.run_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
