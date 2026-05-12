from datetime import date

import pytest
from selenium.common.exceptions import TimeoutException

from web import downloader


class FakeInput:
    def __init__(self):
        self.value = ""

    def clear(self):
        self.value = ""

    def send_keys(self, value):
        self.value = value


class FakeButton:
    def __init__(self, on_click=None):
        self.on_click = on_click

    def click(self):
        if self.on_click:
            self.on_click()


class FakeDriver:
    def __init__(self, pages):
        self.pages = pages
        self.page_index = -1
        self.get_calls = 0
        self.current_url = ""
        self.title = ""
        self.page_source = ""
        self.username_input = FakeInput()
        self.password_input = FakeInput()
        self.switch_to = type("SwitchTo", (), {})()

    def get(self, url):
        self.get_calls += 1
        self.page_index += 1
        page = self.pages[self.page_index]
        self.current_url = page.get("current_url", url)
        self.title = page.get("title", "")
        self.page_source = page.get("page_source", "")

    def find_element(self, by, value):
        if value == "LoginForm[username]":
            return self.username_input
        if value == "LoginForm[password]":
            return self.password_input
        if value == "yt0":
            return FakeButton()
        if value in {"from", "to"}:
            return FakeInput()
        raise AssertionError(f"Elemento inesperado: {value}")

    def find_elements(self, by, value):
        page = self.pages[self.page_index]
        if value == "LoginForm[username]":
            return [self.username_input] if page.get("username_visible", False) else []
        if value == "LoginForm[password]":
            return [self.password_input] if page.get("password_visible", False) else []
        return []


class ImmediateWait:
    def __init__(self, driver, timeout):
        self.driver = driver
        self.timeout = timeout

    def until(self, condition):
        result = condition(self.driver)
        if not result:
            raise TimeoutException("timeout")
        return result


def test_login_reintenta_y_termina_exitosamente(monkeypatch):
    driver = FakeDriver(
        [
            {
                "current_url": "https://example.com/login",
                "page_source": "ERR_CONNECTION_RESET",
                "username_visible": True,
                "password_visible": True,
            },
            {
                "current_url": "https://example.com/home",
                "page_source": "<html>ok</html>",
                "username_visible": False,
                "password_visible": False,
            },
        ]
    )

    monkeypatch.setattr(downloader, "WebDriverWait", ImmediateWait)

    downloader.login(driver, "https://example.com/login", "usr", "pwd", max_retries=3)

    assert driver.get_calls == 2


def test_login_falla_rapido_con_credenciales_invalidas(monkeypatch):
    driver = FakeDriver(
        [
            {
                "current_url": "https://example.com/login",
                "page_source": "Credenciales inválidas",
                "username_visible": True,
                "password_visible": True,
            }
        ]
    )

    monkeypatch.setattr(downloader, "WebDriverWait", ImmediateWait)

    with pytest.raises(downloader.AuthenticationError):
        downloader.login(driver, "https://example.com/login", "usr", "pwd", max_retries=3)

    assert driver.get_calls == 1


def test_exportar_dataset_clasifica_timeout_como_sitio_caido(monkeypatch):
    driver = FakeDriver(
        [
            {
                "current_url": "https://example.com/dataset",
                "page_source": "<html>ok</html>",
            }
        ]
    )

    class TimeoutWait:
        def __init__(self, driver, timeout):
            self.driver = driver
            self.timeout = timeout

        def until(self, condition):
            raise TimeoutException("timeout")

    monkeypatch.setattr(downloader, "WebDriverWait", TimeoutWait)

    with pytest.raises(downloader.SiteUnavailableError):
        downloader.exportar_dataset(driver, "https://example.com/dataset", date(2026, 1, 1), date(2026, 1, 2))


def test_exportar_dataset_detecta_sin_datos(monkeypatch):
    driver = FakeDriver(
        [
            {
                "current_url": "https://example.com/dataset",
                "page_source": "<html>No se encontraron registros</html>",
            }
        ]
    )

    class ClickableWait:
        def __init__(self, driver, timeout):
            self.driver = driver
            self.timeout = timeout

        def until(self, condition):
            if self.timeout == 3:
                raise TimeoutException("sin alert")
            if self.timeout == 10:
                return FakeButton()
            return condition(self.driver)

    monkeypatch.setattr(downloader, "WebDriverWait", ClickableWait)

    with pytest.raises(downloader.NoDataForRangeError):
        downloader.exportar_dataset(driver, "https://example.com/dataset", date(2026, 1, 1), date(2026, 1, 1))
