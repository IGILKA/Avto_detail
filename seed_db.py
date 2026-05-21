import os
import django
import sys

# Set up Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_system.settings')
django.setup()

from django.db import connection
from core.models import EdiniziIzmerenia, Dolzhnosti, Sotrudniki, Budget, Syrie, GotovayaProdukcia, Ingredienty
from django.utils import timezone

def seed_data():
    with connection.cursor() as cursor:
        # 1. Единицы измерения
        if EdiniziIzmerenia.objects.count() == 0:
            print("Seeding Units...")
            for name in ['кг', 'шт', 'литр', 'метр']:
                cursor.execute("INSERT INTO [Производство].[ЕдиницыИзмерения] (Наименование) VALUES (%s)", [name])

        # 2. Должности
        if Dolzhnosti.objects.count() == 0:
            print("Seeding Positions...")
            for name in ['Директор', 'Мастер цеха', 'Закупщик', 'Продавец']:
                cursor.execute("INSERT INTO [Производство].[Должности] (Должность) VALUES (%s)", [name])

        # 3. Бюджет
        if Budget.objects.count() == 0:
            print("Seeding Budget...")
            cursor.execute("INSERT INTO [Производство].[Бюджет] (СуммаБюджета) VALUES (%s)", [1000000.0])

        # 4. Сотрудники
        if Sotrudniki.objects.count() == 0:
            pos_id = cursor.execute("SELECT TOP 1 ИД FROM [Производство].[Должности]").fetchone()[0]
            print("Seeding Employees...")
            cursor.execute("INSERT INTO [Производство].[Сотрудники] (ФИО, ИД_Должности, ЗаработнаяПлата, Адрес, Телефон) VALUES (%s, %s, %s, %s, %s)", 
                           ['Иванов Иван Иванович', pos_id, 50000.0, 'ул. Ленина 1', '89001234567'])

        # 5. Сырье
        if Syrie.objects.count() == 0:
            u_id = cursor.execute("SELECT TOP 1 ИД FROM [Производство].[ЕдиницыИзмерения]").fetchone()[0]
            print("Seeding Raw Materials...")
            cursor.execute("INSERT INTO [Производство].[Сырье] (Наименование, ИД_ЕдИзм, Количество, Сумма) VALUES (%s, %s, %s, %s)", 
                           ['Сталь листовая', u_id, 100.0, 50000.0])

        # 6. Готовая продукция
        if GotovayaProdukcia.objects.count() == 0:
            u_id = cursor.execute("SELECT TOP 1 ИД FROM [Производство].[ЕдиницыИзмерения]").fetchone()[0]
            print("Seeding Finished Goods...")
            cursor.execute("INSERT INTO [Производство].[ГотоваяПродукция] (Наименование, ИД_ЕдИзм, Количество, Сумма) VALUES (%s, %s, %s, %s)", 
                           ['Корпус фары', u_id, 0.0, 0.0])

        # 7. Ингредиенты (Рецепт)
        if Ingredienty.objects.count() == 0:
            prod_id = cursor.execute("SELECT TOP 1 ИД FROM [Производство].[ГотоваяПродукция]").fetchone()[0]
            mat_id = cursor.execute("SELECT TOP 1 ИД FROM [Производство].[Сырье]").fetchone()[0]
            print("Seeding Ingredients (Recipe)...")
            cursor.execute("INSERT INTO [Производство].[Ингредиенты] (ИД_Продукции, ИД_Сырья, Количество) VALUES (%s, %s, %s)", 
                           [prod_id, mat_id, 2.5]) # 2.5 единицы сырья на 1 ед продукции

    print("Seeding completed.")

if __name__ == "__main__":
    seed_data()
