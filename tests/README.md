# Selenium-тесты для avto_detail (Практическая работа №5)

## Установка

```powershell
pip install selenium pytest
```

Chrome у тебя уже есть, ChromeDriver Selenium 4.x качает автоматически.

## Запуск

**1.** Запустить Django-сервер в одном окне терминала:
```powershell
cd "C:\Users\Asus\OneDrive\Рабочий стол\avto_detail"
python manage.py runserver
```

**2.** В другом окне терминала запустить тесты:
```powershell
cd "C:\Users\Asus\OneDrive\Рабочий стол\avto_detail"
pytest tests/ -v
```

## Что покрывают тесты

- `test_auth.py` — регистрация, логин, неверный пароль, logout
- `test_navigation.py` — доступность страниц, защита `/requests/` от анонимов

## JMeter (нагрузочное тестирование)

JMeter скачать с https://jmeter.apache.org — это отдельная GUI-программа.
1. Открыть JMeter
2. Создать Test Plan → Thread Group (50 / 100 / 1000 пользователей)
3. Добавить HTTP Request (host=127.0.0.1, port=8000, path=/reports/ и т.п.)
4. Добавить Aggregate Report (Add → Listener)
5. Запустить, скопировать цифры в отчёт
