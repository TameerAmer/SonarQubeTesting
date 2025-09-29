import os
import json
import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

try:
	# webdriver-manager makes local development easier by auto-downloading drivers
	from webdriver_manager.chrome import ChromeDriverManager
except Exception:
	ChromeDriverManager = None


@pytest.fixture(scope="session")
def base_url(pytestconfig):
	"""Base URL for the application under test. Prefer CLI option, then env var, then default."""
	return (
		pytestconfig.getoption("--base-url")
		or os.environ.get("BASE_URL")
		or "http://localhost:9000"
	)


def pytest_addoption(parser):
	parser.addoption(
		"--base-url",
		action="store",
		default=None,
		help="Base URL for the application under test (overrides BASE_URL env var)",
	)
	parser.addoption(
		"--headless",
		action="store_true",
		default=False,
		help="Run browsers in headless mode",
	)
	parser.addoption(
		"--browser",
		action="store",
		default="chrome",
		help="Browser to use (chrome).",
	)


@pytest.fixture(scope="function")
def driver(request, pytestconfig):
	"""Create a WebDriver instance for tests and attach helpful artifacts on failure.

	- Uses Chrome by default and webdriver-manager if available.
	- Honors the --headless flag or HEADLESS env var.
	- Attaches screenshot, page source and browser logs to Allure on failures.
	"""

	browser = pytestconfig.getoption("--browser") or os.environ.get("BROWSER", "chrome")
	headless_flag = pytestconfig.getoption("--headless") or (
		os.environ.get("HEADLESS", "false").lower() == "true"
	)

	if browser.lower() != "chrome":
		raise RuntimeError(f"Only chrome is supported in this conftest (requested: {browser})")

	options = Options()
	# reduce noise in CI
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	if headless_flag:
		options.add_argument("--headless=new" if hasattr(Options(), "add_argument") else "--headless")

	# enable logging for browser console if possible
	try:
		from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

		caps = DesiredCapabilities.CHROME.copy()
		caps["goog:loggingPrefs"] = {"browser": "ALL"}
	except Exception:
		caps = None

	driver = None
	try:
		if ChromeDriverManager:
			service = Service(ChromeDriverManager().install())
			if caps:
				driver = webdriver.Chrome(service=service, options=options, desired_capabilities=caps)
			else:
				driver = webdriver.Chrome(service=service, options=options)
		else:
			# Fallback: rely on chromedriver being in PATH
			if caps:
				driver = webdriver.Chrome(options=options, desired_capabilities=caps)
			else:
				driver = webdriver.Chrome(options=options)
	except Exception as e:
		# Re-raise with a clearer message
		raise RuntimeError(
			"Failed to create Chrome WebDriver. Ensure Chrome/Chromedriver are installed or install webdriver-manager. Original error: "
			+ str(e)
		)

	# Make driver accessible on the node for hooks
	request.node.driver = driver

	yield driver

	# Teardown handled here; attachments on failure are performed in pytest_runtest_makereport hook
	try:
		driver.quit()
	except Exception:
		pass


def _attach_browser_state(node, driver):
	"""Best-effort attachments: screenshot, page source, current URL/title, and browser logs."""
	try:
		if driver:
			try:
				png = driver.get_screenshot_as_png()
				allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)
			except Exception:
				pass

			try:
				src = driver.page_source
				allure.attach(src, name="page_source", attachment_type=allure.attachment_type.HTML)
			except Exception:
				pass

			try:
				url = driver.current_url
				title = driver.title
				allure.attach(f"URL: {url}\nTitle: {title}", name="page_info", attachment_type=allure.attachment_type.TEXT)
			except Exception:
				pass

			# browser logs (may not be available in all environments)
			try:
				logs = []
				if hasattr(driver, "get_log"):
					for entry in driver.get_log("browser"):
						logs.append(entry)
				if logs:
					allure.attach(json.dumps(logs, default=str, indent=2), name="browser_logs", attachment_type=allure.attachment_type.JSON)
			except Exception:
				pass
	except Exception:
		# swallow any unexpected errors during best-effort attachments
		pass


def pytest_configure(config):
	# Add some environment properties visible in the Allure report
	try:
		os.makedirs("allure-results", exist_ok=True)
		env_file = os.path.join("allure-results", "environment.properties")
		with open(env_file, "w") as f:
			f.write("Test.Framework=SonarQube UI Selenium+Pytest\n")
			ci_env = os.getenv("CI", "false").lower()
			platform = "CI" if ci_env == "true" else "Local"
			f.write(f"CI.Platform={platform}\n")
			f.write("Test.Types=UI Automation\n")
			f.write("Tooling=Allure Report\n")
			# Extract branch name from GITHUB_REF if present (e.g., refs/heads/feature-branch -> feature-branch)
			# Prefer GITHUB_HEAD_REF for PRs, otherwise extract branch name from GITHUB_REF
			branch = os.getenv('GIT_BRANCH')
			github_head_ref = os.getenv('GITHUB_HEAD_REF')
			github_ref = os.getenv('GITHUB_REF', '')
			if not branch:
				if github_head_ref:
					branch = github_head_ref
				elif github_ref:
					branch = github_ref.split('/')[-1]
				else:
					branch = 'local'
			f.write(f"GIT_BRANCH={branch}\n")
			f.write(f"CI={os.getenv('CI', 'false')}\n")
			f.write(f"PYTHON_VERSION={os.getenv('PYTHON_VERSION', '') or str(os.sys.version)}\n")

			for key in [
				"BASE_URL",
				"SONARQUBE_URL",
				"SONARQUBE_USERNAME",
				"IMAGE_TAG",
				"HEADLESS",
			]:
				val = os.getenv(key)
				if val:
					f.write(f"{key}={val}\n")
	except Exception:
		pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_call(item):
	"""Set dynamic Allure parameters/labels per-test from environment vars."""
	api_base = os.environ.get("BASE_URL")
	image_tag = os.environ.get("IMAGE_TAG")
	sonar = os.environ.get("SONARQUBE_URL")

	if api_base:
		try:
			allure.dynamic.parameter("base_url", api_base)
			allure.dynamic.label("base_url", api_base)
		except Exception:
			pass
	if image_tag:
		try:
			allure.dynamic.parameter("image_tag", image_tag)
			allure.dynamic.label("image_tag", image_tag)
		except Exception:
			pass
	if sonar:
		try:
			allure.dynamic.parameter("sonarqube_url", sonar)
			allure.dynamic.label("sonarqube", sonar)
		except Exception:
			pass

	yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
	# Hook to attach screenshot, page source, console logs and traceback when a test fails
	outcome = yield
	rep = outcome.get_result()
	if rep.when == "call" and rep.failed:
		driver = getattr(item, "driver", None) or getattr(item, "_driver", None) or getattr(item, "_request", None)
		# request.node.driver is the more reliable location
		try:
			driver = getattr(item, "driver", None) or getattr(item, "_driver", None) or getattr(item, "_request", None) or getattr(item, "node", None) or None
		except Exception:
			driver = None

		# Try common places where we stored the driver
		if not driver:
			driver = getattr(item, "_driver", None) or getattr(item, "driver", None) or getattr(getattr(item, 'node', None), 'driver', None)

		# Best-effort attach
		try:
			_attach_browser_state(item, getattr(item, "driver", None) or getattr(item, "node", None) and getattr(item.node, "driver", None))
		except Exception:
			pass

		# Attach the traceback/longrepr
		try:
			longrepr = rep.longreprtext if hasattr(rep, "longreprtext") else str(rep.longrepr)
			allure.attach(longrepr, name="traceback", attachment_type=allure.attachment_type.TEXT)
		except Exception:
			pass
