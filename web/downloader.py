import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging


logger = logging.getLogger("scraper_contable")


def iniciar_driver(download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    options = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True
    }

    options.add_experimental_option("prefs", prefs)

    options.add_argument("--start-maximized")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--ignore-certificate-errors")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": os.path.abspath(download_dir)
        }
    )

    return driver


def login(driver, login_url, username, password):
    driver.get(login_url)

    # AJUSTAR SELECTORES SEG?N LA WEB REAL
    driver.find_element(By.NAME, "LoginForm[username]").send_keys(username)
    driver.find_element(By.NAME, "LoginForm[password]").send_keys(password)
    driver.find_element(By.NAME, "yt0").click()

    logger.info("Logueado como %s", username)


def logout(driver, logout_url):
    driver.get(logout_url)
    logger.info("Logout realizado")


def exportar_dataset(driver, dataset_url, fecha_desde, fecha_hasta):
    driver.get(dataset_url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "from"))
    )

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "to"))
    )

    fecha_desde_str = fecha_desde.strftime("%d/%m/%Y")
    fecha_hasta_str = fecha_hasta.strftime("%d/%m/%Y")

    from_input = driver.find_element(By.ID, "from")
    from_input.clear()

    to_input = driver.find_element(By.ID, "to")
    to_input.clear()

    from_input.send_keys(fecha_desde_str)
    to_input.send_keys(fecha_hasta_str)

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "yt1"))
    ).click()

    logger.info("Export solicitado desde %s hasta %s", fecha_desde, fecha_hasta)

    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        mensaje = alert.text
        alert.accept()
        raise Exception(f"Error del sistema: {mensaje}")
    except:
        pass
