"""
Создаёт схему [Производство] и все таблицы в Car_detail,
затем заполняет начальными данными.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_system.settings')
django.setup()

from django.db import connection

def run_sql(sql, desc=""):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        print(f"  OK  {desc}")
    except Exception as e:
        print(f"  ERR {desc}: {e}")

print("=== 1. Создание схемы Производство ===")
run_sql("""
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = N'Производство')
    EXEC(N'CREATE SCHEMA [Производство]')
""", "Схема Производство")

print("\n=== 2. Создание таблиц ===")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'ЕдиницыИзмерения')
CREATE TABLE [Производство].[ЕдиницыИзмерения] (
    [ИД]            INT IDENTITY(1,1) PRIMARY KEY,
    [Наименование]  NVARCHAR(50) NOT NULL
)
""", "ЕдиницыИзмерения")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'Должности')
CREATE TABLE [Производство].[Должности] (
    [ИД]        INT IDENTITY(1,1) PRIMARY KEY,
    [Должность] NVARCHAR(100) NOT NULL
)
""", "Должности")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'Сотрудники')
CREATE TABLE [Производство].[Сотрудники] (
    [ИД]               INT IDENTITY(1,1) PRIMARY KEY,
    [ФИО]              NVARCHAR(200) NOT NULL,
    [ИД_Должности]     INT NOT NULL REFERENCES [Производство].[Должности]([ИД]),
    [ЗаработнаяПлата]  FLOAT NOT NULL,
    [Адрес]            NVARCHAR(300) NULL,
    [Телефон]          NVARCHAR(30)  NULL
)
""", "Сотрудники")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'Бюджет')
CREATE TABLE [Производство].[Бюджет] (
    [ИД]           INT IDENTITY(1,1) PRIMARY KEY,
    [СуммаБюджета] FLOAT NOT NULL
)
""", "Бюджет")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'Сырье')
CREATE TABLE [Производство].[Сырье] (
    [ИД]            INT IDENTITY(1,1) PRIMARY KEY,
    [Наименование]  NVARCHAR(150) NOT NULL,
    [ИД_ЕдИзм]      INT NOT NULL REFERENCES [Производство].[ЕдиницыИзмерения]([ИД]),
    [Количество]    FLOAT NOT NULL DEFAULT 0,
    [Сумма]         FLOAT NOT NULL DEFAULT 0
)
""", "Сырье")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'ГотоваяПродукция')
CREATE TABLE [Производство].[ГотоваяПродукция] (
    [ИД]            INT IDENTITY(1,1) PRIMARY KEY,
    [Наименование]  NVARCHAR(150) NOT NULL,
    [ИД_ЕдИзм]      INT NOT NULL REFERENCES [Производство].[ЕдиницыИзмерения]([ИД]),
    [Количество]    FLOAT NOT NULL DEFAULT 0,
    [Сумма]         FLOAT NOT NULL DEFAULT 0
)
""", "ГотоваяПродукция")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'Ингредиенты')
CREATE TABLE [Производство].[Ингредиенты] (
    [ИД]           INT IDENTITY(1,1) PRIMARY KEY,
    [ИД_Продукции] INT NOT NULL REFERENCES [Производство].[ГотоваяПродукция]([ИД]),
    [ИД_Сырья]     INT NOT NULL REFERENCES [Производство].[Сырье]([ИД]),
    [Количество]   FLOAT NOT NULL
)
""", "Ингредиенты")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'ЗакупкаСырья')
CREATE TABLE [Производство].[ЗакупкаСырья] (
    [ИД]           INT IDENTITY(1,1) PRIMARY KEY,
    [ИД_Сырья]     INT NOT NULL REFERENCES [Производство].[Сырье]([ИД]),
    [Количество]   FLOAT NOT NULL,
    [Сумма]        FLOAT NOT NULL,
    [Дата]         DATETIME NOT NULL,
    [ИД_Сотрудника] INT NOT NULL REFERENCES [Производство].[Сотрудники]([ИД])
)
""", "ЗакупкаСырья")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'ПроизводствоПродукции')
CREATE TABLE [Производство].[ПроизводствоПродукции] (
    [ИД]            INT IDENTITY(1,1) PRIMARY KEY,
    [ИД_Продукции]  INT NOT NULL REFERENCES [Производство].[ГотоваяПродукция]([ИД]),
    [Количество]    FLOAT NOT NULL,
    [Дата]          DATETIME NOT NULL,
    [ИД_Сотрудника] INT NOT NULL REFERENCES [Производство].[Сотрудники]([ИД])
)
""", "ПроизводствоПродукции")

run_sql("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
               WHERE TABLE_SCHEMA=N'Производство' AND TABLE_NAME=N'ПродажаПродукции')
CREATE TABLE [Производство].[ПродажаПродукции] (
    [ИД]            INT IDENTITY(1,1) PRIMARY KEY,
    [ИД_Продукции]  INT NOT NULL REFERENCES [Производство].[ГотоваяПродукция]([ИД]),
    [Количество]    FLOAT NOT NULL,
    [Сумма]         FLOAT NOT NULL,
    [Дата]          DATETIME NOT NULL,
    [ИД_Сотрудника] INT NOT NULL REFERENCES [Производство].[Сотрудники]([ИД])
)
""", "ПродажаПродукции")

print("\n=== 3. Начальные данные ===")

# Единицы измерения
run_sql("""
IF NOT EXISTS (SELECT 1 FROM [Производство].[ЕдиницыИзмерения])
BEGIN
    SET IDENTITY_INSERT [Производство].[ЕдиницыИзмерения] ON
    INSERT INTO [Производство].[ЕдиницыИзмерения] ([ИД],[Наименование]) VALUES
        (1, N'шт'), (2, N'кг'), (3, N'м'), (4, N'л'), (5, N'комп.')
    SET IDENTITY_INSERT [Производство].[ЕдиницыИзмерения] OFF
END
""", "ЕдиницыИзмерения — данные")

# Должности
run_sql("""
IF NOT EXISTS (SELECT 1 FROM [Производство].[Должности])
BEGIN
    SET IDENTITY_INSERT [Производство].[Должности] ON
    INSERT INTO [Производство].[Должности] ([ИД],[Должность]) VALUES
        (1, N'Директор'),
        (2, N'Закупщик'),
        (3, N'Мастер цеха'),
        (4, N'Продавец')
    SET IDENTITY_INSERT [Производство].[Должности] OFF
END
""", "Должности — данные")

# Сотрудники
run_sql("""
IF NOT EXISTS (SELECT 1 FROM [Производство].[Сотрудники])
BEGIN
    SET IDENTITY_INSERT [Производство].[Сотрудники] ON
    INSERT INTO [Производство].[Сотрудники] ([ИД],[ФИО],[ИД_Должности],[ЗаработнаяПлата],[Адрес],[Телефон]) VALUES
        (1, N'Иванов Иван Иванович',    1, 80000, N'г. Бишкек, ул. Ленина 1',  N'+996 700 000001'),
        (2, N'Петров Пётр Петрович',    2, 45000, N'г. Бишкек, ул. Токтогула 5',N'+996 700 000002'),
        (3, N'Сидоров Сергей Сергеевич',3, 55000, N'г. Бишкек, ул. Манаса 10', N'+996 700 000003'),
        (4, N'Козлова Анна Викторовна', 4, 40000, N'г. Бишкек, ул. Чуй 22',    N'+996 700 000004')
    SET IDENTITY_INSERT [Производство].[Сотрудники] OFF
END
""", "Сотрудники — данные")

# Бюджет
run_sql("""
IF NOT EXISTS (SELECT 1 FROM [Производство].[Бюджет])
BEGIN
    SET IDENTITY_INSERT [Производство].[Бюджет] ON
    INSERT INTO [Производство].[Бюджет] ([ИД],[СуммаБюджета]) VALUES (1, 500000)
    SET IDENTITY_INSERT [Производство].[Бюджет] OFF
END
""", "Бюджет — данные")

# Сырьё
run_sql("""
IF NOT EXISTS (SELECT 1 FROM [Производство].[Сырье])
BEGIN
    SET IDENTITY_INSERT [Производство].[Сырье] ON
    INSERT INTO [Производство].[Сырье] ([ИД],[Наименование],[ИД_ЕдИзм],[Количество],[Сумма]) VALUES
        (1, N'Сталь листовая',   2, 500, 75000),
        (2, N'Резина листовая',  2, 200, 30000),
        (3, N'Алюминий',         2, 300, 60000),
        (4, N'Пластик технический',2,150, 18000),
        (5, N'Болты М8 (упак.)', 5, 100, 5000),
        (6, N'Смазка техническая',4, 50,  4000),
        (7, N'Краска автомобильная',4,80, 16000)
    SET IDENTITY_INSERT [Производство].[Сырье] OFF
END
""", "Сырьё — данные")

# Готовая продукция
run_sql("""
IF NOT EXISTS (SELECT 1 FROM [Производство].[ГотоваяПродукция])
BEGIN
    SET IDENTITY_INSERT [Производство].[ГотоваяПродукция] ON
    INSERT INTO [Производство].[ГотоваяПродукция] ([ИД],[Наименование],[ИД_ЕдИзм],[Количество],[Сумма]) VALUES
        (1, N'Тормозной диск',      1, 0, 0),
        (2, N'Глушитель выхлопной', 1, 0, 0),
        (3, N'Бампер передний',     1, 0, 0),
        (4, N'Рычаг подвески',      1, 0, 0)
    SET IDENTITY_INSERT [Производство].[ГотоваяПродукция] OFF
END
""", "ГотоваяПродукция — данные")

# Ингредиенты (рецептура)
run_sql("""
IF NOT EXISTS (SELECT 1 FROM [Производство].[Ингредиенты])
BEGIN
    SET IDENTITY_INSERT [Производство].[Ингредиенты] ON
    INSERT INTO [Производство].[Ингредиенты] ([ИД],[ИД_Продукции],[ИД_Сырья],[Количество]) VALUES
        -- Тормозной диск: 3кг стали, 0.5кг резины, болты 1упак.
        (1, 1, 1, 3),
        (2, 1, 2, 0.5),
        (3, 1, 5, 1),
        -- Глушитель: 4кг стали, 1кг алюминия, смазка 0.3л
        (4, 2, 1, 4),
        (5, 2, 3, 1),
        (6, 2, 6, 0.3),
        -- Бампер: 2кг пластика, краска 0.5л
        (7, 3, 4, 2),
        (8, 3, 7, 0.5),
        -- Рычаг подвески: 2кг стали, 0.3кг алюминия, болты 2упак.
        (9, 4, 1, 2),
        (10,4, 3, 0.3),
        (11,4, 5, 2)
    SET IDENTITY_INSERT [Производство].[Ингредиенты] OFF
END
""", "Ингредиенты — данные")

print("\n=== Готово! ===")
print("Все таблицы созданы и заполнены начальными данными.")
