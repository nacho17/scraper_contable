import logging
import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


logger = logging.getLogger("scraper_contable")


class AuthenticationError(Exception):
    pass


class SiteUnavailableError(Exception):
    pass


class DownloadBlockedError(Exception):
    pass


def iniciar_driver(download_dir, headless=False):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    options = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
    }

    options.add_experimental_option("prefs", prefs)

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--safebrowsing-disable-download-protection")
    options.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.set_page_load_timeout(30)

    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": os.path.abspath(download_dir),
        },
    )

    return driver


def login(driver, login_url, username, password, max_retries=3):
    ultimo_error = None

    for intento in range(1, max_retries + 1):
        try:
            _abrir_url(driver, login_url, "login")

            usuario_input = driver.find_element(By.NAME, "LoginForm[username]")
            password_input = driver.find_element(By.NAME, "LoginForm[password]")

            usuario_input.clear()
            password_input.clear()
            usuario_input.send_keys(username)
            password_input.send_keys(password)
            driver.find_element(By.NAME, "yt0").click()

            WebDriverWait(driver, 10).until(
                lambda d: _login_invalido(d) or _login_exitoso(d) or _pagina_indisponible(d)
            )

            mensaje_sitio = _mensaje_pagina_indisponible(driver)
            if mensaje_sitio:
                raise SiteUnavailableError(
                    f"La web no responde correctamente durante el login: {mensaje_sitio}"
                )

            if _login_invalido(driver):
                raise AuthenticationError("Credenciales inválidas o vencidas.")

            if _login_exitoso(driver):
                logger.info("Logueado como %s en intento %s", username, intento)
                return

            raise SiteUnavailableError("No se pudo confirmar el resultado del login.")
        except AuthenticationError:
            raise
        except (SiteUnavailableError, TimeoutException, WebDriverException) as exc:
            ultimo_error = _normalizar_error_sitio(exc, "login")
            logger.warning(
                "Fallo de login para %s en intento %s/%s: %s",
                username,
                intento,
                max_retries,
                ultimo_error,
            )

            if intento == max_retries:
                raise ultimo_error

    if ultimo_error:
        raise ultimo_error

    raise SiteUnavailableError("No se pudo completar el login.")


def _login_invalido(driver):
    page_text = (driver.page_source or "").lower()
    error_keywords = (
        "credenciales inválidas",
        "credenciales invalidas",
        "usuario o contraseña incorrect",
        "usuario o contrasena incorrect",
        "login incorrect",
        "invalid credentials",
        "incorrect username",
        "incorrect password",
    )

    return any(keyword in page_text for keyword in error_keywords)


def _login_exitoso(driver):
    current_url = (driver.current_url or "").lower()
    sigue_en_login = "login" in current_url or "signin" in current_url

    return not sigue_en_login and not driver.find_elements(By.NAME, "LoginForm[username]")


def _pagina_indisponible(driver):
    return _mensaje_pagina_indisponible(driver) is not None


def _mensaje_pagina_indisponible(driver):
    partes = [
        (getattr(driver, "title", "") or "").lower(),
        (getattr(driver, "current_url", "") or "").lower(),
        (getattr(driver, "page_source", "") or "").lower(),
    ]
    contenido = "\n".join(partes)

    errores = (
        "this site can’t be reached",
        "this site can't be reached",
        "err_connection",
        "err_name_not_resolved",
        "err_timed_out",
        "err_ssl",
        "502 bad gateway",
        "503 service unavailable",
        "504 gateway timeout",
        "service unavailable",
        "site maintenance",
        "temporarily unavailable",
        "no se puede acceder a este sitio",
        "tardó demasiado en responder",
    )

    for error in errores:
        if error in contenido:
            return error

    return None


def _normalizar_error_sitio(exc, contexto):
    if isinstance(exc, SiteUnavailableError):
        return exc

    return SiteUnavailableError(
        f"La web no responde correctamente durante {contexto}: {exc}"
    )


def _abrir_url(driver, url, contexto):
    try:
        driver.get(url)
    except (TimeoutException, WebDriverException) as exc:
        raise _normalizar_error_sitio(exc, contexto) from exc

    mensaje_sitio = _mensaje_pagina_indisponible(driver)
    if mensaje_sitio:
        raise SiteUnavailableError(
            f"La web no responde correctamente durante {contexto}: {mensaje_sitio}"
        )


def logout(driver, logout_url):
    driver.get(logout_url)
    logger.info("Logout realizado")


def exportar_dataset(driver, dataset_url, fecha_desde, fecha_hasta):
    _abrir_url(driver, dataset_url, "la apertura del dataset")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "from"))
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "to"))
        )
    except TimeoutException as exc:
        raise SiteUnavailableError(
            "La web no cargó a tiempo la pantalla de exportación del dataset."
        ) from exc

    fecha_desde_str = fecha_desde.strftime("%d/%m/%Y")
    fecha_hasta_str = fecha_hasta.strftime("%d/%m/%Y")

    from_input = driver.find_element(By.ID, "from")
    to_input = driver.find_element(By.ID, "to")

    from_input.clear()
    to_input.clear()
    from_input.send_keys(fecha_desde_str)
    to_input.send_keys(fecha_hasta_str)

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "yt1"))
        ).click()
    except TimeoutException as exc:
        raise SiteUnavailableError(
            "La web no habilitó a tiempo el botón de exportación."
        ) from exc

    logger.info("Export solicitado desde %s hasta %s", fecha_desde, fecha_hasta)

    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        mensaje = alert.text
        alert.accept()
        raise SiteUnavailableError(f"Error del sistema durante la exportación: {mensaje}")
    except TimeoutException:
        return
