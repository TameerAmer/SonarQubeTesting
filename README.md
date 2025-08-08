# SonarQubeTesting

This repository contains automated API and UI tests for a SonarQube instance.

## Project Structure

```
SonarQubeTesting/
├── API_Testing/         # API tests (requests, pytest)
│   ├── test_authentication.py
│   ├── test_health.py
│   ├── test_projects.py
│   └── __init__.py
├── UI_Testing/          # UI tests (Selenium, pytest)
│   ├── test_delete_project.py
│   ├── test_login_logout.py
│   ├── pages.py         # Page Object Model classes
│   └── __init__.py
├── requirements.txt     # Python dependencies
└── .github/workflows/   # GitHub Actions workflows
```

## Getting Started

### Prerequisites
- Python 3.11 or 3.12
- Google Chrome (for UI tests)
- ChromeDriver (matching your Chrome version)
- SonarQube server running (locally or remote)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/TameerAmer/SonarQubeTesting.git
   cd SonarQubeTesting
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running API Tests
Make sure your SonarQube server is running and accessible.

```sh
pytest API_Testing/ --cov=API_Testing --cov-report=term-missing
```

### Running UI Tests
Make sure Chrome and ChromeDriver are installed. The UI tests use Selenium and the Page Object Model.

```sh
pytest UI_Testing/ --cov=UI_Testing --cov-report=term-missing
```

To run UI tests in headless mode (recommended for CI):
```sh
HEADLESS=true pytest UI_Testing/
```

### GitHub Actions CI
- Automated tests run on every pull request to the `master` branch.
- See `.github/workflows/test.yml` and `.github/workflows/ui-testing.yaml` for details.

## Environment Variables
- `BASE_URL`: The URL of your SonarQube server (default: `http://localhost:9000`).
- `HEADLESS`: Set to `true` to run Selenium tests in headless mode.

## Contributing
Feel free to open issues or pull requests for improvements or bug fixes.

