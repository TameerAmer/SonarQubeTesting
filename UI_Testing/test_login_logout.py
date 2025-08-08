
import unittest
import sys
import os
#for the debug mode, i had to add this line to ensure the parent directory is included in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Adjust the path to include the parent directory
from selenium import webdriver
from UI_Testing.pages import LoginPage
from selenium.webdriver.chrome.options import Options

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:9000')  # Default to localhost if not set

class TestLoginLogout(unittest.TestCase):
    def setUp(self):
        if os.environ.get("HEADLESS", "false").lower() == "true":
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = webdriver.Chrome()
        self.driver.get(BASE_URL)
        self.driver.get(BASE_URL)
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        self.login_page = LoginPage(self.driver)

    def test_page_title(self):
        self.assertIn("SonarQube", self.driver.title)

    def test_login(self):
        self.login_page.login("admin", "Mypassword1?")
        self.assertTrue(self.login_page.is_logo_displayed())
        self.login_page.open_profile()
        self.login_page.go_to_my_account()
        self.assertEqual(self.login_page.get_logged_in_username(), "admin")

    def test_logout(self):
        self.login_page.login("admin", "Mypassword1?")
        self.login_page.logout()
        self.assertTrue(self.login_page.is_login_page_displayed())

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()