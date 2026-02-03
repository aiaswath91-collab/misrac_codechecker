import requests
import sys
import os
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path

class MISRAAPITester:
    def __init__(self, base_url="https://misra-analyzer.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.analysis_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if data and not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=60)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=60)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_test_zip(self):
        """Create a test ZIP file with C code"""
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "test_code.zip")
        
        # Create test C file with MISRA violations
        test_c_code = """
#include <stdio.h>

int unused_var;  // MISRA violation: unused variable

int main() {
    int x;  // MISRA violation: uninitialized variable
    printf("Hello World\\n");
    return x;  // MISRA violation: returning uninitialized variable
}
"""
        
        c_file_path = os.path.join(temp_dir, "test.c")
        with open(c_file_path, 'w') as f:
            f.write(test_c_code)
        
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(c_file_path, "test.c")
        
        return zip_path

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_file_upload(self):
        """Test file upload endpoint"""
        zip_path = self.create_test_zip()
        
        try:
            with open(zip_path, 'rb') as f:
                files = {'file': ('test_code.zip', f, 'application/zip')}
                success, response = self.run_test(
                    "File Upload",
                    "POST",
                    "upload",
                    200,
                    files=files
                )
                
                if success and 'analysis_id' in response:
                    self.analysis_id = response['analysis_id']
                    print(f"   Analysis ID: {self.analysis_id}")
                    return True
                return False
        finally:
            # Cleanup
            try:
                os.remove(zip_path)
                os.rmdir(os.path.dirname(zip_path))
            except:
                pass

    def test_invalid_file_upload(self):
        """Test upload with non-ZIP file"""
        temp_dir = tempfile.mkdtemp()
        txt_path = os.path.join(temp_dir, "test.txt")
        
        try:
            with open(txt_path, 'w') as f:
                f.write("This is not a ZIP file")
            
            with open(txt_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                success, response = self.run_test(
                    "Invalid File Upload (Non-ZIP)",
                    "POST",
                    "upload",
                    400,
                    files=files
                )
                return success
        finally:
            try:
                os.remove(txt_path)
                os.rmdir(temp_dir)
            except:
                pass

    def test_analysis_status(self):
        """Test analysis status endpoint"""
        if not self.analysis_id:
            print("❌ No analysis ID available for status check")
            return False
        
        success, response = self.run_test(
            "Analysis Status",
            "GET",
            f"analysis/{self.analysis_id}",
            200
        )
        
        if success:
            status = response.get('status')
            print(f"   Analysis Status: {status}")
            
            # Wait for analysis to complete if it's running
            import time
            max_wait = 60  # 60 seconds max wait
            wait_time = 0
            
            while status in ['pending', 'running'] and wait_time < max_wait:
                print(f"   Waiting for analysis to complete... ({wait_time}s)")
                time.sleep(5)
                wait_time += 5
                
                success, response = self.run_test(
                    f"Analysis Status Check ({wait_time}s)",
                    "GET",
                    f"analysis/{self.analysis_id}",
                    200
                )
                
                if success:
                    status = response.get('status')
                    print(f"   Current Status: {status}")
                else:
                    break
            
            return success and status in ['completed', 'failed']
        
        return False

    def test_analysis_status_not_found(self):
        """Test analysis status with invalid ID"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        success, response = self.run_test(
            "Analysis Status (Not Found)",
            "GET",
            f"analysis/{fake_id}",
            404
        )
        return success

    def test_report_download(self):
        """Test report download endpoint"""
        if not self.analysis_id:
            print("❌ No analysis ID available for report download")
            return False
        
        # First check if analysis is completed
        success, response = self.run_test(
            "Check Analysis Before Report Download",
            "GET",
            f"analysis/{self.analysis_id}",
            200
        )
        
        if not success or response.get('status') != 'completed':
            print(f"❌ Analysis not completed, status: {response.get('status')}")
            return False
        
        # Test report download
        url = f"{self.api_url}/report/{self.analysis_id}"
        print(f"\n🔍 Testing Report Download...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            success = response.status_code == 200
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type')}")
                print(f"   Content-Length: {len(response.content)} bytes")
                
                # Check if it's HTML content
                if 'html' in response.headers.get('content-type', '').lower():
                    content = response.text
                    if 'MISRA C:2012 Compliance Report' in content:
                        print("   ✅ HTML report contains expected title")
                    else:
                        print("   ⚠️  HTML report missing expected title")
                
                return True
            else:
                print(f"❌ Failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
        finally:
            self.tests_run += 1

    def test_list_analyses(self):
        """Test list analyses endpoint"""
        success, response = self.run_test(
            "List Analyses",
            "GET",
            "analyses",
            200
        )
        
        if success:
            analyses = response if isinstance(response, list) else []
            print(f"   Found {len(analyses)} analyses")
            
            if self.analysis_id:
                # Check if our analysis is in the list
                found = any(a.get('id') == self.analysis_id for a in analyses)
                if found:
                    print(f"   ✅ Our analysis {self.analysis_id} found in list")
                else:
                    print(f"   ⚠️  Our analysis {self.analysis_id} not found in list")
        
        return success

def main():
    """Run all API tests"""
    print("🚀 Starting MISRA C Analyzer API Tests")
    print("=" * 50)
    
    tester = MISRAAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Invalid File Upload", tester.test_invalid_file_upload),
        ("File Upload", tester.test_file_upload),
        ("Analysis Status", tester.test_analysis_status),
        ("Analysis Status Not Found", tester.test_analysis_status_not_found),
        ("Report Download", tester.test_report_download),
        ("List Analyses", tester.test_list_analyses),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                print(f"\n⚠️  Test '{test_name}' failed but continuing...")
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.analysis_id:
        print(f"🔗 Analysis ID for manual testing: {tester.analysis_id}")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    return 0 if success_rate >= 70 else 1

if __name__ == "__main__":
    sys.exit(main())