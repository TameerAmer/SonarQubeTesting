import os
import unittest
import requests
from requests.auth import HTTPBasicAuth

class TestAuthentication(unittest.TestCase):

    BASE_URL = os.environ.get("BASE_URL", "http://localhost:9000")
    AUTH = HTTPBasicAuth("admin", "Mypassword1?")
    


    def test_success_login(self):
        #login
        myData={"login":"admin","password":"Mypassword1?"}
        res = requests.post(f"{self.BASE_URL}/api/authentication/login", data=myData)  
        self.assertEqual(res.status_code, 200)
        #access health endpoint after login
        res2 = requests.get(f"{self.BASE_URL}/api/system/health", auth=self.AUTH) 
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json().get("health"),"GREEN")
    
    def test_bad_login(self):
        myData={"login":"WrongName","password":"WrongPass"}
        res = requests.post(f"{self.BASE_URL}/api/authentication/login", data=myData)  
        self.assertEqual(res.status_code, 401)


    def test_logout(self):
        session = requests.Session()
        # Step 1: Login and validate session
        validate = session.post(f"{self.BASE_URL}/api/authentication/login", auth=self.AUTH)
        self.assertTrue(validate.status_code,200)

        # Step 2: Logout using session
        logout = session.post(f"{self.BASE_URL}/api/authentication/logout")
        self.assertEqual(logout.status_code, 200)

        # Step 3: Try accessing protected resource after logout
        after_logout = session.get(f"{self.BASE_URL}/api/system/health")
        self.assertEqual(after_logout.status_code, 403) #the request was understood by the server but forbidden
        

if __name__ == "__main__":
    unittest.main()
