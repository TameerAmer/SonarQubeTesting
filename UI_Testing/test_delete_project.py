import sys
import os
#for the debug mode, i had to add this line to ensure the parent directory is included in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Adjust the path to include the parent directory

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from UI_Testing.pages import LoginPage, ProjectPage



BASE_URL = "http://localhost:9000" 

class TestCreateDeleteProject(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get(BASE_URL)
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)

    def test_create_delete_project(self):
        # Log in to SonarQube
        login_page = LoginPage(self.driver)
        login_page.login("admin", "Mypassword1?")
        self.assertTrue(login_page.is_logo_displayed())

        # Use ProjectPage for project creation and deletion
        project_page = ProjectPage(self.driver)
        project_page.go_to_projects()
        project_page.start_create_project()
        project_page.fill_project_details("My Project", "MY_PROJECT")
        project_page.next_step()
        project_page.select_global_settings()
        project_page.create_project()
        success_message = project_page.wait_for_success_message()
        self.assertIn("Your project has been created.", success_message.text)

        # Navigate to the project page and verify
        project_page.go_to_projects()
        self.assertTrue(self.driver.find_element(By.XPATH, "//a[normalize-space()='My Project']").is_displayed())
        project_page.open_project("My Project")
        project_page.open_project_settings()
        project_page.start_delete_project()
        project_page.confirm_delete_project()
        success_toast = project_page.wait_for_delete_success()
        self.assertIn('Project "My Project" has been successfully deleted.', success_toast.text)

    def tearDown(self):
        self.driver.quit()
        

if __name__ == "__main__":
    unittest.main()