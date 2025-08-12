import os
import unittest
import requests
from requests.auth import HTTPBasicAuth

class TestProjects(unittest.TestCase):
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:9000")
    AUTH = HTTPBasicAuth("admin", "Mypassword1?")
    PROJECT_NAME = "MyProject"
    PROJECT_KEY = "my_project"

    def setUp(self):
        """Ensure a clean start by deleting the project if it exists."""
        self.delete_project(self.PROJECT_KEY)

    def tearDown(self):
        """Clean up after each test."""
        self.delete_project(self.PROJECT_KEY)
        self.delete_project("newKey")  # cleanup from update_key tests

    # ---------- Helper Methods ----------
    def create_project(self, name=None, key=None):
        """Create a project in SonarQube."""
        data = {
            "name": name or self.PROJECT_NAME,
            "project": key or self.PROJECT_KEY
        }
        return requests.post(f"{self.BASE_URL}/api/projects/create", data=data, auth=self.AUTH)

    def delete_project(self, key):
        """Delete a project from SonarQube."""
        return requests.post(f"{self.BASE_URL}/api/projects/delete", data={"project": key}, auth=self.AUTH)

    def search_projects(self):
        """Search all projects."""
        return requests.get(f"{self.BASE_URL}/api/projects/search", auth=self.AUTH)

    def update_key(self, old_key, new_key):
        """Update project key."""
        return requests.post(f"{self.BASE_URL}/api/projects/update_key", data={"from": old_key, "to": new_key}, auth=self.AUTH)

    def update_visibility(self, key, visibility):
        """Update project visibility."""
        return requests.post(f"{self.BASE_URL}/api/projects/update_visibility", data={"project": key, "visibility": visibility}, auth=self.AUTH)

    # ---------- Tests ----------
    def test_create_search_delete_project(self):
        # Create
        res1 = self.create_project()
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["project"]["name"], self.PROJECT_NAME)

        # Search
        res2 = self.search_projects()
        self.assertEqual(res2.status_code, 200)
        project_names = [p["name"] for p in res2.json()["components"]]
        self.assertIn(self.PROJECT_NAME, project_names)

        # Delete
        res3 = self.delete_project(self.PROJECT_KEY)
        self.assertEqual(res3.status_code, 204)

        # Verify deletion
        res4 = self.search_projects()
        self.assertNotIn(self.PROJECT_NAME, [p["name"] for p in res4.json()["components"]])

    def test_delete_a_not_found_proj(self):
        res = self.delete_project("NotExist")
        self.assertEqual(res.status_code, 404)

    def test_update_key(self):
        self.create_project()
        res2 = self.update_key(self.PROJECT_KEY, "newKey")
        self.assertEqual(res2.status_code, 204)
        self.assertEqual(self.delete_project("newKey").status_code, 204)

    def test_update_a_non_existing_key(self):
        res = self.update_key("NotExist", "newKey")
        self.assertEqual(res.status_code, 404)

    def test_update_visibility(self):
        self.create_project()
        res = self.update_visibility(self.PROJECT_KEY, "private")
        self.assertEqual(res.status_code, 204)

if __name__ == "__main__":
    unittest.main()
