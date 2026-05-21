"""
Нагрузочное тестирование avto_detail.

Запуск:
    locust -f tests/locustfile.py --host=http://127.0.0.1:8000

Затем открыть http://localhost:8089 и задать:
    - Number of users: 50 / 100 / 1000
    - Ramp up: 10 (за сколько секунд набрать всех пользователей)

После теста — кнопка "Download Data" → скачать CSV или сделать скриншот
таблицы Statistics (она и есть Aggregate Report).
"""
from locust import HttpUser, task, between
import uuid
import re


class AnonymousUser(HttpUser):
    """Виртуальный пользователь без авторизации."""
    wait_time = between(1, 3)   # пауза между запросами 1-3 сек

    @task(3)
    def home(self):
        self.client.get("/")

    @task(3)
    def login_page(self):
        self.client.get("/accounts/login/", name="GET /accounts/login/")

    @task(2)
    def reports(self):
        # /reports/ требует staff, но любой может попытаться (Broken Access Control из лабы 4)
        self.client.get("/reports/", name="GET /reports/")

    @task(2)
    def zakupki_list(self):
        self.client.get("/zakupki/", name="GET /zakupki/")

    @task(2)
    def requests_list(self):
        # /requests/ требует логин — анонимы получат редирект 302
        self.client.get("/requests/", name="GET /requests/")


# Класс AuthenticatedUser удалён — параллельные регистрации перегружают
# SQLite (Database is locked) и dev-сервер Django. Для чистых GET-замеров
# хватает AnonymousUser выше. Если нужен POST-нагрузочный тест — лучше
# поднять gunicorn + PostgreSQL.
