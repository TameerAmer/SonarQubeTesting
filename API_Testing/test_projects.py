import os
import unittest
import requests
from requests.auth import HTTPBasicAuth

class TestProjects(unittest.TestCase):

    BASE_URL = os.environ.get("BASE_URL", "http://localhost:9000")
   
    AUTH = HTTPBasicAuth("admin", "Mypassword1?")
    project_data={"name":"MyProject","project":"my_project"}

    def test_create_search_delete_project(self):
        #create a project first
        res1 = requests.post(f"{self.BASE_URL}/api/projects/create", data=self.project_data, auth=self.AUTH)  
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json().get("project").get("name"),"MyProject")
    
        #search for the proj
        res2 = requests.get(f"{self.BASE_URL}/api/projects/search", auth=self.AUTH)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json().get("components")[0].get("name"),"MyProject")

        #delete the project
        res3 = requests.post(f"{self.BASE_URL}/api/projects/delete",data={"project":"my_project"}, auth=self.AUTH)
        self.assertEqual(res3.status_code, 204)

        #try to search again after deletion
        res4 = requests.get(f"{self.BASE_URL}/api/projects/search", auth=self.AUTH)
        self.assertEqual(res4.status_code, 200)
        for i in range(len(res4.json().get("components"))):
            self.assertNotEqual("MyProject",res4.json().get("components")[i].get("name"))

    def test_delete_a_not_found_proj(self):
        res = requests.post(f"{self.BASE_URL}/api/projects/delete",data={"project":"NotExist"}, auth=self.AUTH)
        self.assertEqual(res.status_code, 404)

    def test_update_key(self):
        res1 = requests.post(f"{self.BASE_URL}/api/projects/create", data=self.project_data, auth=self.AUTH)  
        self.assertEqual(res1.status_code, 200)
        res2 = requests.post(f"{self.BASE_URL}/api/projects/update_key",data={"from":"my_project","to":"newKey"}, auth=self.AUTH)
        self.assertEqual(res2.status_code, 204)
        res3 = requests.post(f"{self.BASE_URL}/api/projects/delete",data={"project":"newKey"}, auth=self.AUTH)
        self.assertEqual(res3.status_code, 204)
    
    def test_update_a_non_existing_key(self):
        res2 = requests.post(f"{self.BASE_URL}/api/projects/update_key",data={"from":"NotExist","to":"newKey"}, auth=self.AUTH)
        self.assertEqual(res2.status_code, 404)

    def test_update_visibility(self):
        res1 = requests.post(f"{self.BASE_URL}/api/projects/create", data=self.project_data, auth=self.AUTH)  
        self.assertEqual(res1.status_code, 200)
        res2 = requests.post(f"{self.BASE_URL}/api/projects/update_visibility",data={"project":"my_project","visibility":"private"}, auth=self.AUTH)
        self.assertEqual(res2.status_code, 204)
        res3 = requests.post(f"{self.BASE_URL}/api/projects/delete",data={"project":"my_project"}, auth=self.AUTH)
        self.assertEqual(res3.status_code, 204)

if __name__ == "__main__":
    unittest.main()
