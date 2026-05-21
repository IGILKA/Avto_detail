"""Тесты доступности страниц и базовой навигации."""
from selenium.webdriver.common.by import By


def test_home_page(driver, base_url):
    """TC-08: главная страница доступна без авторизации."""
    driver.get(f"{base_url}/")
    assert driver.title  # любой непустой title


def test_login_page_loads(driver, base_url):
    """TC-09: страница логина загружается с формой."""
    driver.get(f"{base_url}/accounts/login/")
    assert driver.find_element(By.ID, "id_username")
    assert driver.find_element(By.ID, "id_password")


def test_register_page_loads(driver, base_url):
    """TC-10: страница регистрации загружается."""
    driver.get(f"{base_url}/register/")
    assert driver.find_element(By.ID, "id_username")
    assert driver.find_element(By.ID, "id_password1")
    assert driver.find_element(By.ID, "id_password2")


def test_requests_requires_login(driver, base_url):
    """TC-11: /requests/ редиректит анонима на логин."""
    driver.delete_all_cookies()
    driver.get(f"{base_url}/requests/")
    assert "/login" in driver.current_url


def test_zayavki_create_page(driver, base_url, logged_in_user):
    """TC-12: авторизованный пользователь видит форму подачи заявки."""
    driver.get(f"{base_url}/requests/new/")
    assert driver.find_element(By.NAME, "produkcia")
    assert driver.find_element(By.NAME, "quantity")
