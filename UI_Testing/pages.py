from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "login-input")
        self.password_input = (By.ID, "password-input")
        self.logo = (By.XPATH, "//a[@aria-label='Link to home page']")
        self.profile_button = (By.ID, "dropdown-menu-trigger")
        self.my_account_button = (By.XPATH, "//div[@dir='ltr']//a[1]")
        self.logout_button = (By.XPATH, "//div[@dir='ltr']//a[2]")
        self.login_title = (By.XPATH, "//h1[normalize-space()='Log in to SonarQube']")
        self.login_span = (By.XPATH, "//span[@id='login']")

    def is_on_login_page(self):
        return "SonarQube" in self.driver.title

    def login(self, username, password):
        self.driver.find_element(*self.username_input).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.password_input).send_keys(Keys.RETURN)

    def is_logo_displayed(self):
        return self.driver.find_element(*self.logo).is_displayed()

    def open_profile(self):
        self.driver.find_element(*self.profile_button).click()

    def go_to_my_account(self):
        self.driver.find_element(*self.my_account_button).click()

    def get_logged_in_username(self):
        return self.driver.find_element(*self.login_span).text

    def logout(self):
        self.open_profile()
        self.driver.find_element(*self.logout_button).click()

    def is_login_page_displayed(self):
        return self.driver.find_element(*self.login_title).is_displayed()
    
class ProjectPage:
    def __init__(self, driver):
        self.driver = driver
        self.projects_button = (By.XPATH, "//a[normalize-space()='Projects']")
        self.create_project_menu = (By.ID, "project-creation-menu-trigger")
        self.local_project_button = (By.XPATH, "//a[normalize-space()='Local project']")
        self.project_name_input = (By.ID, "project-name")
        self.project_key_input = (By.ID, "project-key")
        self.next_button = (By.XPATH, "//button[@type='submit']")
        self.radio_button_global_settings = (By.XPATH, "//input[@value='general']")
        self.create_project_button = (By.XPATH, "//span[contains(@class,'sw-mb-8') and contains(@class,'en2lust1')]//button[@type='submit']")
        self.success_message = (By.XPATH, "//*[contains(text(), 'Your project has been created.')]")
        self.project_link = lambda name: (By.XPATH, f"//a[normalize-space()='{name}']")
        self.project_settings_button = (By.ID, "component-navigation-admin-trigger")
        self.deletion_button_1 = (By.XPATH, "//a[@data-component='render-deletion-link']")
        self.deletion_button_2 = (By.ID, "delete-project")
        self.delete_modal = (By.XPATH, "//div[@role='alertdialog' and contains(., 'Delete Project')]")
        self.delete_button_3 = (By.XPATH, ".//button[.//span[text()='Delete']]")
        self.success_toast = (By.XPATH, "//*[contains(text(), 'has been successfully deleted.')]")

    def go_to_projects(self):
        self.driver.find_element(*self.projects_button).click()

    def start_create_project(self):
        self.driver.find_element(*self.create_project_menu).click()
        self.driver.find_element(*self.local_project_button).click()

    def fill_project_details(self, name, key):
        self.driver.find_element(*self.project_name_input).send_keys(name)
        key_input = self.driver.find_element(*self.project_key_input)
        key_input.clear()
        key_input.send_keys(key)

    def next_step(self):
        self.driver.find_element(*self.next_button).click()

    def select_global_settings(self):
        self.driver.find_element(*self.radio_button_global_settings).click()

    def create_project(self):
        self.driver.find_element(*self.create_project_button).click()

    def wait_for_success_message(self, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(self.success_message))

    def open_project(self, name):
        self.driver.find_element(*self.project_link(name)).click()

    def open_project_settings(self):
        self.driver.find_element(*self.project_settings_button).click()

    def start_delete_project(self):
        self.driver.find_element(*self.deletion_button_1).click()
        self.driver.find_element(*self.deletion_button_2).click()

    def confirm_delete_project(self, timeout=10):
        modal = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.delete_modal))
        modal.find_element(*self.delete_button_3).click()

    def wait_for_delete_success(self, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.success_toast)
        )
