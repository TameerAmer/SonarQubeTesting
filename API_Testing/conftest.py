import os
import json
import allure
import pytest
import requests
from requests.auth import HTTPBasicAuth


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default=None,
        help="Base URL for API tests (overrides BASE_URL env var)",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    """Return the base URL for API tests.

    Priority: --base-url cli option > BASE_URL env var > default http://localhost:9000
    """
    return (
        pytestconfig.getoption("--base-url")
        or os.environ.get("BASE_URL")
        or "http://localhost:9000"
    )


@pytest.fixture(scope="session")
def auth():
    """Provide an HTTPBasicAuth object for admin user when needed."""
    user = os.environ.get("API_USER", "admin")
    pwd = os.environ.get("API_PASS", "Mypassword1?")
    return HTTPBasicAuth(user, pwd)


class ApiSessionWrapper:
    """Wrap requests.Session to auto-attach requests/responses to Allure.

    Usage in tests: pass the `api` fixture and call `api.get('/api/..')` — the
    wrapper will preprend the base_url and attach the request+response JSON to Allure.
    """

    def __init__(self, base_url: str):
        self._base = base_url.rstrip("/")
        self._session = requests.Session()
        self.last_response = None

    def request(self, method, path, **kwargs):
        url = path if path.startswith("http") else f"{self._base}{path if path.startswith('/') else '/' + path}"
        resp = self._session.request(method, url, **kwargs)
        self.last_response = resp
        self._attach_response(method, url, kwargs, resp)
        return resp

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def _attach_response(self, method, url, req_kwargs, resp):
        try:
            # Build a compact JSON-friendly object with request/response details
            attach = {
                "method": method,
                "url": url,
                "request_headers": {k: v for k, v in (req_kwargs.get("headers") or {}).items()},
                "request_params": req_kwargs.get("params"),
                "request_json": req_kwargs.get("json"),
                "request_data": req_kwargs.get("data"),
                "status_code": resp.status_code,
            }
            # Try to parse JSON response body, otherwise include text (trimmed)
            try:
                attach["response_body"] = resp.json()
            except Exception:
                attach["response_text"] = (resp.text[:10000] + "...") if len(resp.text) > 10000 else resp.text

            allure.attach(
                json.dumps(attach, default=str, indent=2),
                name=f"{method} {url}",
                attachment_type=allure.attachment_type.JSON,
            )
        except Exception:
            # best-effort; do not raise
            pass


@pytest.fixture
def api(base_url, request):
    """Provide an ApiSessionWrapper for tests and expose the last response on the node.

    Tests can use `api.get('/api/system/health', auth=auth)` or pass full URLs.
    """
    session = ApiSessionWrapper(base_url)

    # attach the wrapper to the test node so hooks can find last_response on failure
    request.node.api_session = session
    try:
        yield session
    finally:
        try:
            session._session.close()
        except Exception:
            pass


def pytest_configure(config):
    # write environment.properties for Allure
    try:
        os.makedirs("allure-results", exist_ok=True)
        env_file = os.path.join("allure-results", "environment.properties")
        with open(env_file, "w") as f:
            f.write("Test.Framework=Requests+Pytest\n")
            f.write(f"GIT_BRANCH={os.getenv('GIT_BRANCH', os.getenv('GITHUB_REF', 'local'))}\n")
            f.write(f"CI={os.getenv('CI', 'false')}\n")
            f.write(f"PYTHON_VERSION={os.getenv('PYTHON_VERSION', '') or str(os.sys.version)}\n")
            for key in ["BASE_URL", "API_USER", "API_PASS", "IMAGE_TAG"]:
                val = os.getenv(key)
                if val:
                    f.write(f"{key}={val}\n")
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_call(item):
    """Add dynamic Allure parameters from environment before each test runs."""
    base = os.environ.get("BASE_URL")
    image = os.environ.get("IMAGE_TAG")
    if base:
        try:
            allure.dynamic.parameter("base_url", base)
            allure.dynamic.label("base_url", base)
        except Exception:
            pass
    if image:
        try:
            allure.dynamic.parameter("image_tag", image)
            allure.dynamic.label("image_tag", image)
        except Exception:
            pass

    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        # Attach the last API response (if any) to Allure for debugging
        try:
            session = getattr(item, "api_session", None) or getattr(item.node, "api_session", None)
            if session and getattr(session, "last_response", None):
                resp = session.last_response
                try:
                    body = None
                    try:
                        body = json.dumps(resp.json(), default=str, indent=2)
                        atype = allure.attachment_type.JSON
                    except Exception:
                        body = resp.text
                        atype = allure.attachment_type.TEXT
                    allure.attach(body, name=f"last_api_response_{resp.status_code}", attachment_type=atype)
                except Exception:
                    pass
        except Exception:
            pass
