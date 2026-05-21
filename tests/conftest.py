"""Pytest + Selenium fixtures для тестирования avto_detail."""
import pytest
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def driver():
    opts = Options()
    # Включить headless через переменную окружения HEADLESS=1.
    # По умолчанию — браузер видно (демо-режим для защиты).
    import os
    if os.environ.get("HEADLESS") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1500,1000")
    opts.add_argument("--start-maximized")
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


@pytest.fixture(autouse=True)
def clean_session(driver):
    """Очищаем cookies перед каждым тестом — анонимный старт всегда."""
    driver.get(BASE_URL)          # сначала открыть домен, иначе delete_all_cookies не сработает
    driver.delete_all_cookies()


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def unique_username():
    return f"test_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def logged_in_user(driver, base_url, unique_username):
    """Регистрируем нового пользователя и возвращаем его username."""
    driver.get(f"{base_url}/register/")
    driver.find_element(By.ID, "id_username").send_keys(unique_username)
    driver.find_element(By.ID, "id_password1").send_keys("StrongPass2026!")
    driver.find_element(By.ID, "id_password2").send_keys("StrongPass2026!")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    # подождать редирект после регистрации
    WebDriverWait(driver, 5).until(EC.url_contains("/requests"))
    return unique_username
