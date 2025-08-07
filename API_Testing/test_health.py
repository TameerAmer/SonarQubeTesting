import os
import unittest
import requests
from requests.auth import HTTPBasicAuth

class TestSonarHealth(unittest.TestCase):

    BASE_URL = os.environ.get("BASE_URL", "http://localhost:9000")
    AUTH = HTTPBasicAuth("admin", "Mypassword1?")


    def test_health(self):
        res = requests.get(f"{self.BASE_URL}/api/system/health", auth=self.AUTH)  
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("health"),"GREEN")
    
    def test_unauth_health(self):
        res = requests.get(f"{self.BASE_URL}/api/system/health")  
        self.assertEqual(res.status_code, 403)

if __name__ == "__main__":
    unittest.main()
