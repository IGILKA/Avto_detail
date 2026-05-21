"""
Заполняет Car_detail реалистичной историей операций
(закупки, производство, продажи, заявки, кредиты).
"""
import os, django, random
from datetime import timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enterprise_system.settings')
django.setup()

from django.utils import timezone
from django.db import transaction
from core.models import (
    Syrie, GotovayaProdukcia, Sotrudniki, Budget, Ingredienty,
    ZakupkaSyrya, ProizvodstvoProdukcii, ProdazhaProdukcii,
    Kredit, ZayavkiNaProizvodstvo,
)

now = timezone.now()
def days_ago(n, h=None):
    t = now - timedelta(days=n)
    if h is not None:
        t = t.replace(hour=h, minute=random.randint(0, 59))
    return t

print("=== Очистка старых операций ===")
ZayavkiNaProizvodstvo.objects.all().delete()
ProdazhaProdukcii.objects.all().delete()
ProizvodstvoProdukcii.objects.all().delete()
ZakupkaSyrya.objects.all().delete()
Kredit.objects.all().delete()
print("  очищено")

# Восстановим состояние сырья и продукции до базового
print("\n=== Сброс склада ===")
base_syrie = {
    1: (500, 75000),   # Сталь
    2: (200, 30000),   # Резина
    3: (300, 60000),   # Алюминий
    4: (150, 18000),   # Пластик
    5: (100, 5000),    # Болты
    6: (50,  4000),    # Смазка
    7: (80,  16000),   # Краска
}
for sid, (q, a) in base_syrie.items():
    Syrie.objects.filter(id=sid).update(quantity=q, amount=a)
GotovayaProdukcia.objects.all().update(quantity=0, amount=0)
Budget.objects.filter(id=1).update(amount=500000)
print("  сырьё и бюджет восстановлены")

# Получаем сотрудников по ролям
director  = Sotrudniki.objects.get(id=1)
zakupshik = Sotrudniki.objects.get(id=2)
master    = Sotrudniki.objects.get(id=3)
prodavec  = Sotrudniki.objects.get(id=4)

budget = Budget.objects.get(id=1)

print("\n=== 1. Закупки сырья (10 операций) ===")
purchases = [
    (1, 100, 14500, 55, zakupshik),  # сталь
    (2,  50,  7200, 50, zakupshik),  # резина
    (3,  80, 15500, 45, zakupshik),  # алюминий
    (1, 150, 22000, 40, director),   # сталь
    (4,  60,  7000, 35, zakupshik),  # пластик
    (5,  30,  1450, 30, zakupshik),  # болты
    (7,  40,  7800, 25, zakupshik),  # краска
    (2,  80, 11500, 20, zakupshik),  # резина
    (6,  20,  1600, 15, zakupshik),  # смазка
    (3,  50,  9700, 10, director),   # алюминий
]
for sid, qty, amt, days, emp in purchases:
    s = Syrie.objects.get(id=sid)
    s.quantity += qty
    s.amount   += amt
    s.save()
    budget.amount -= amt
    ZakupkaSyrya.objects.create(
        id_syrya=s, quantity=qty, amount=amt,
        date=days_ago(days, 10 + random.randint(0,6)),
        id_sotrudnika=emp,
    )
budget.save()
print(f"  создано: {ZakupkaSyrya.objects.count()} закупок")

print("\n=== 2. Производство (8 операций) ===")
productions = [
    (1, 30, 50, master),   # тормозной диск
    (2, 20, 45, master),   # глушитель
    (3, 15, 40, master),   # бампер
    (4, 25, 35, master),   # рычаг
    (1, 40, 28, master),   # ещё тормозной диск
    (3, 20, 22, director), # ещё бампер
    (2, 25, 15, master),   # ещё глушитель
    (4, 30,  8, master),   # ещё рычаг
]
for pid, qty, days, emp in productions:
    prod = GotovayaProdukcia.objects.get(id=pid)
    ingredients = Ingredienty.objects.filter(id_produkcii=prod).select_related('id_syrya')
    total_cost = 0
    enough = True
    for ing in ingredients:
        needed = ing.quantity * qty
        if ing.id_syrya.quantity < needed:
            enough = False
            break
    if not enough:
        continue
    for ing in ingredients:
        needed = ing.quantity * qty
        cpu = ing.id_syrya.amount / ing.id_syrya.quantity if ing.id_syrya.quantity > 0 else 0
        ing.id_syrya.quantity -= needed
        ing.id_syrya.amount   -= cpu * needed
        ing.id_syrya.save()
        total_cost += cpu * needed
    prod.quantity += qty
    prod.amount   += total_cost
    prod.save()
    ProizvodstvoProdukcii.objects.create(
        id_produkcii=prod, quantity=qty,
        date=days_ago(days, 13 + random.randint(0,4)),
        id_sotrudnika=emp,
    )
print(f"  создано: {ProizvodstvoProdukcii.objects.count()} операций")

print("\n=== 3. Продажи (12 операций) ===")
sales = [
    (1, 20, 42, prodavec),
    (2, 15, 38, prodavec),
    (3, 10, 32, prodavec),
    (4, 20, 30, prodavec),
    (1, 25, 24, prodavec),
    (2, 18, 20, director),
    (3, 12, 16, prodavec),
    (4, 22, 12, prodavec),
    (1, 15,  9, prodavec),
    (2,  8,  6, prodavec),
    (3,  8,  4, prodavec),
    (4, 15,  2, prodavec),
]
for pid, qty, days, emp in sales:
    prod = GotovayaProdukcia.objects.get(id=pid)
    if prod.quantity < qty:
        continue
    cpu = prod.amount / prod.quantity if prod.quantity > 0 else 0
    revenue = round(cpu * 1.30 * qty, 2)
    prod.quantity -= qty
    prod.amount   -= cpu * qty
    prod.save()
    budget.amount += revenue
    ProdazhaProdukcii.objects.create(
        id_produkcii=prod, quantity=qty, amount=revenue,
        date=days_ago(days, 15 + random.randint(0,4)),
        id_sotrudnika=emp,
    )
budget.save()
print(f"  создано: {ProdazhaProdukcii.objects.count()} продаж")

print("\n=== 4. Кредиты ===")
# Один погашенный
k1 = Kredit.objects.create(amount=50000, is_paid=True)
Kredit.objects.filter(id=k1.id).update(date_taken=days_ago(60))
# Два активных
k2 = Kredit.objects.create(amount=100000, is_paid=False)
Kredit.objects.filter(id=k2.id).update(date_taken=days_ago(30))
k3 = Kredit.objects.create(amount=75000,  is_paid=False)
Kredit.objects.filter(id=k3.id).update(date_taken=days_ago(7))
print(f"  создано: {Kredit.objects.count()} кредитов (1 погашен, 2 активных)")

print("\n=== 5. Заявки на производство ===")
# Несколько выполненных заявок
zayavki_data = [
    ('director', 1, 5, 'Выполнена', 45),
    ('admin',    2, 3, 'Выполнена', 30),
    ('director', 3, 2, 'Выполнена', 20),
    ('admin',    4, 4, 'Выполнена', 10),
    ('director', 1, 8, 'Ошибка',    5),
    ('admin',    2, 2, 'Создана',   1),
]
for fio, pid, qty, status, days in zayavki_data:
    prod = GotovayaProdukcia.objects.get(id=pid)
    z = ZayavkiNaProizvodstvo.objects.create(
        applicant_fio=fio, id_produkcii=prod, quantity=qty, status=status,
        rejection_reason='Недостаточно средств в бюджете для закупки' if status == 'Ошибка' else None,
    )
    # сдвигаем дату создания на нужное число дней назад
    ZayavkiNaProizvodstvo.objects.filter(id=z.id).update(
        created_at=days_ago(days), updated_at=days_ago(days-1 if days>1 else 0),
    )
print(f"  создано: {ZayavkiNaProizvodstvo.objects.count()} заявок")

print("\n=== ИТОГ ===")
print(f"Бюджет:      {Budget.objects.first().amount:.2f} сом")
print(f"Закупок:     {ZakupkaSyrya.objects.count()}")
print(f"Производств: {ProizvodstvoProdukcii.objects.count()}")
print(f"Продаж:      {ProdazhaProdukcii.objects.count()}")
print(f"Заявок:      {ZayavkiNaProizvodstvo.objects.count()}")
print(f"Кредитов:    {Kredit.objects.count()}")
print("\nГотово! Зайди под admin/admin123 и посмотри отчёты.")
