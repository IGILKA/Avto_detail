# Нагрузочное тестирование Locust

## Установка

```powershell
pip install locust
```

## Запуск

**Окно 1** — Django-сервер (как для Selenium):
```powershell
cd "C:\Users\Asus\OneDrive\Рабочий стол\avto_detail"
python manage.py runserver
```

**Окно 2** — Locust:
```powershell
cd "C:\Users\Asus\OneDrive\Рабочий стол\avto_detail"
locust -f tests/locustfile.py --host=http://127.0.0.1:8000
```

Открыть в браузере: **http://localhost:8089**

## Сценарий для отчёта — три прогона

Нужно сделать **3 запуска** с разными параметрами и скриншот таблицы Statistics после каждого:

| Прогон | Number of users | Ramp up | Run time |
|---|---|---|---|
| 1 | **50**  | 10 | 60 s  |
| 2 | **100** | 10 | 60 s  |
| 3 | **1000**| 10 | 60 s  |

В UI Locust:
1. Заполни Number of users + Ramp up
2. Нажми **Start**
3. Подожди ~1 мин
4. Нажми **Stop**
5. На вкладке **Statistics** скопируй цифры (`# requests`, `Avg`, `Min`, `Max`, `Median`, `90%ile`, `Fails`, `RPS`) → это твой Aggregate Report

Можно также скачать CSV: кнопка **Download Data → Download requests statistics CSV**.

## Что покрывает

- `AnonymousUser` — стучится в /, /accounts/login/, /reports/, /zakupki/, /requests/
- `AuthenticatedUser` — регистрируется и подаёт заявку на производство (полный пайплайн)

## Если нужен только JMeter

Если препод хочет именно JMeter (Java), то:
1. Скачать с https://jmeter.apache.org/
2. Запустить `bin/jmeter.bat`
3. File → New → Test Plan → Add → Thread Group
4. Add → Sampler → HTTP Request (host=127.0.0.1, port=8000, path=/reports/)
5. Add → Listener → Aggregate Report
6. Запустить, скриншотить.

Locust даёт **те же метрики**, что и JMeter (Avg, Min, Max, 90%, throughput, error %).
