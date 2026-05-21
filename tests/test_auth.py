"""Тесты аутентификации: регистрация, логин, неверный пароль, logout."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_user_registration(driver, base_url, unique_username):
    """TC-01: новый пользователь успешно регистрируется и попадает в /requests/."""
    driver.get(f"{base_url}/register/")
    driver.find_element(By.ID, "id_username").send_keys(unique_username)
    driver.find_element(By.ID, "id_password1").send_keys("StrongPass2026!")
    driver.find_element(By.ID, "id_password2").send_keys("StrongPass2026!")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    WebDriverWait(driver, 5).until(EC.url_contains("/requests"))
    assert "/requests" in driver.current_url


def test_user_login(driver, base_url, logged_in_user):
    """TC-02: существующий пользователь логинится корректно."""
    import os, time
    # Демо-паузы — чтобы при показе препод успевал увидеть каждый шаг.
    # При HEADLESS=1 пауз нет (для CI).
    pause = 0 if os.environ.get("HEADLESS") == "1" else 1.0

    driver.delete_all_cookies()
    driver.get(f"{base_url}/accounts/login/")
    time.sleep(pause)

    driver.find_element(By.ID, "id_username").send_keys(logged_in_user)
    time.sleep(pause)
    driver.find_element(By.ID, "id_password").send_keys("StrongPass2026!")
    time.sleep(pause)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    WebDriverWait(driver, 5).until(lambda d: "/login" not in d.current_url)
    time.sleep(pause)
    assert "/requests" in driver.current_url


def test_login_wrong_password(driver, base_url):
    """TC-03: неверный пароль — остаёмся на странице логина."""
    driver.get(f"{base_url}/accounts/login/")
    driver.find_element(By.ID, "id_username").send_keys("nonexistent_user_xyz")
    driver.find_element(By.ID, "id_password").send_keys("wrong_pass_123")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    assert "/login" in driver.current_url or "/accounts/login" in driver.current_url


def test_logout(driver, base_url, logged_in_user):
    """TC-07: после logout (через кнопку в navbar) — редирект на login."""
    # У проекта logout это POST-форма с CSRF (Django 5+ требует POST).
    # Кликаем по кнопке «Выйти» в navbar — это полноценный logout.
    driver.get(f"{base_url}/requests/")  # любая аутентифицированная страница
    logout_btn = driver.find_element(
        By.XPATH, "//form[contains(@action,'logout')]//button"
    )
    logout_btn.click()
    # После выхода защищённая страница должна редиректить на login
    driver.get(f"{base_url}/requests/")
    assert "/login" in driver.current_url
