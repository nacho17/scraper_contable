import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _instalar_stub_selenium():
    selenium = types.ModuleType("selenium")
    webdriver = types.ModuleType("selenium.webdriver")
    webdriver_common = types.ModuleType("selenium.webdriver.common")
    webdriver_common_by = types.ModuleType("selenium.webdriver.common.by")
    webdriver_chrome = types.ModuleType("selenium.webdriver.chrome")
    webdriver_chrome_service = types.ModuleType("selenium.webdriver.chrome.service")
    webdriver_support = types.ModuleType("selenium.webdriver.support")
    webdriver_support_ui = types.ModuleType("selenium.webdriver.support.ui")
    webdriver_support_ec = types.ModuleType("selenium.webdriver.support.expected_conditions")
    selenium_common = types.ModuleType("selenium.common")
    selenium_common_exceptions = types.ModuleType("selenium.common.exceptions")

    class TimeoutException(Exception):
        pass

    class WebDriverException(Exception):
        pass

    class ChromeOptions:
        def __init__(self):
            self.arguments = []
            self.experimental_options = {}

        def add_argument(self, arg):
            self.arguments.append(arg)

        def add_experimental_option(self, key, value):
            self.experimental_options[key] = value

    class Chrome:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def set_page_load_timeout(self, timeout):
            self.timeout = timeout

        def execute_cdp_cmd(self, *args, **kwargs):
            return None

    class Service:
        def __init__(self, executable_path):
            self.executable_path = executable_path

    class By:
        NAME = "name"
        ID = "id"

    class WebDriverWait:
        def __init__(self, driver, timeout):
            self.driver = driver
            self.timeout = timeout

        def until(self, condition):
            return condition(self.driver)

    webdriver.ChromeOptions = ChromeOptions
    webdriver.Chrome = Chrome
    webdriver_common_by.By = By
    webdriver_chrome_service.Service = Service
    webdriver_support_ui.WebDriverWait = WebDriverWait
    webdriver_support_ec.presence_of_element_located = lambda locator: (lambda driver: True)
    webdriver_support_ec.element_to_be_clickable = lambda locator: (lambda driver: True)
    webdriver_support_ec.alert_is_present = lambda: (lambda driver: False)
    selenium_common_exceptions.TimeoutException = TimeoutException
    selenium_common_exceptions.WebDriverException = WebDriverException

    sys.modules["selenium"] = selenium
    sys.modules["selenium.webdriver"] = webdriver
    sys.modules["selenium.webdriver.common"] = webdriver_common
    sys.modules["selenium.webdriver.common.by"] = webdriver_common_by
    sys.modules["selenium.webdriver.chrome"] = webdriver_chrome
    sys.modules["selenium.webdriver.chrome.service"] = webdriver_chrome_service
    sys.modules["selenium.webdriver.support"] = webdriver_support
    sys.modules["selenium.webdriver.support.ui"] = webdriver_support_ui
    sys.modules["selenium.webdriver.support.expected_conditions"] = webdriver_support_ec
    sys.modules["selenium.common"] = selenium_common
    sys.modules["selenium.common.exceptions"] = selenium_common_exceptions

    selenium.webdriver = webdriver
    selenium.common = selenium_common
    webdriver.common = webdriver_common
    webdriver.chrome = webdriver_chrome
    webdriver.support = webdriver_support
    webdriver_common.by = webdriver_common_by
    webdriver_chrome.service = webdriver_chrome_service
    webdriver_support.ui = webdriver_support_ui
    webdriver_support.expected_conditions = webdriver_support_ec
    selenium_common.exceptions = selenium_common_exceptions


def _instalar_stub_webdriver_manager():
    webdriver_manager = types.ModuleType("webdriver_manager")
    webdriver_manager_chrome = types.ModuleType("webdriver_manager.chrome")

    class ChromeDriverManager:
        def install(self):
            return "chromedriver"

    webdriver_manager_chrome.ChromeDriverManager = ChromeDriverManager
    webdriver_manager.chrome = webdriver_manager_chrome

    sys.modules["webdriver_manager"] = webdriver_manager
    sys.modules["webdriver_manager.chrome"] = webdriver_manager_chrome


try:
    import selenium  # noqa: F401
except ModuleNotFoundError:
    _instalar_stub_selenium()

try:
    import webdriver_manager  # noqa: F401
except ModuleNotFoundError:
    _instalar_stub_webdriver_manager()
