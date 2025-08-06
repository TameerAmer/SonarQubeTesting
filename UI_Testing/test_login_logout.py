
import unittest
from selenium import webdriver
from UI_Testing.pages import LoginPage

BASE_URL = "http://localhost:9000"

class TestLoginLogout(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
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