from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from .models import ZakupkaSyrya, Syrie, Sotrudniki, Budget, EdiniziIzmerenia, ProizvodstvoProdukcii, ProdazhaProdukcii, GotovayaProdukcia, Ingredienty, Dolzhnosti, Kredit, ZayavkiNaProizvodstvo

def home(request):
    return render(request, 'core/home.html')

def zakupka_list(request):
    zakupki = ZakupkaSyrya.objects.select_related('id_syrya', 'id_sotrudnika', 'id_syrya__id_edizm').all().order_by('-date')
    return render(request, 'core/zakupka_list.html', {'zakupki': zakupki})

def zakupka_create(request):
    if request.method == 'POST':
        syrie_id = request.POST.get('syrie')
        quantity = float(request.POST.get('quantity'))
        amount = float(request.POST.get('amount'))
        sotrudnik_id = request.POST.get('sotrudnik')
        
        try:
            with transaction.atomic():
                # Проверка должности
                emp = Sotrudniki.objects.select_related('id_dolzhnosti').get(id=sotrudnik_id)
                role_name = emp.id_dolzhnosti.name.lower()
                if 'закупщик' not in role_name and 'директор' not in role_name:
                    messages.error(request, f'Отказано в доступе. Должность "{emp.id_dolzhnosti.name}" не позволяет осуществлять закупки!')
                    return redirect('zakupka_create')
                
                # 1. Списание бюджета
                budget = Budget.objects.first()
                if not budget or budget.amount < amount:
                    messages.error(request, 'Недостаточно средств в бюджете!')
                    return redirect('zakupka_create')
                
                budget.amount -= amount
                budget.save()
                
                # 2. Обновление остатков сырья
                syrie = Syrie.objects.get(id=syrie_id)
                syrie.quantity += quantity
                syrie.amount += amount
                syrie.save()
                
                # 3. Запись транзакции
                ZakupkaSyrya.objects.create(
                    id_syrya_id=syrie_id,
                    quantity=quantity,
                    amount=amount,
                    date=timezone.now(),
                    id_sotrudnika_id=sotrudnik_id
                )
                
                messages.success(request, 'Закупка успешно оформлена!')
                return redirect('zakupka_list')
                
        except Exception as e:
            messages.error(request, f'Ошибка при оформлении: {str(e)}')
            
    syrie = Syrie.objects.all()
    sotrudniki = Sotrudniki.objects.all()
    return render(request, 'core/zakupka_form.html', {
        'syrie': syrie,
        'sotrudniki': sotrudniki
    })

def proizvodstvo_list(request):
    proizvodstvo = ProizvodstvoProdukcii.objects.select_related('id_produkcii', 'id_sotrudnika').all().order_by('-date')
    return render(request, 'core/proizvodstvo_list.html', {'proizvodstvo': proizvodstvo})

def proizvodstvo_create(request):
    if request.method == 'POST':
        produkcia_id = request.POST.get('produkcia')
        quantity = float(request.POST.get('quantity'))
        sotrudnik_id = request.POST.get('sotrudnik')
        
        try:
            with transaction.atomic():
                # Проверка должности
                emp = Sotrudniki.objects.select_related('id_dolzhnosti').get(id=sotrudnik_id)
                role_name = emp.id_dolzhnosti.name.lower()
                if 'мастер' not in role_name and 'директор' not in role_name:
                    messages.error(request, f'Отказано в доступе. Должность "{emp.id_dolzhnosti.name}" не имеет прав мастера цеха для производства!')
                    return redirect('proizvodstvo_create')
                
                # 1. Проверка ингредиентов
                ingredients = Ingredienty.objects.filter(id_produkcii_id=produkcia_id)
                for ing in ingredients:
                    needed = ing.quantity * quantity
                    if ing.id_syrya.quantity < needed:
                        messages.error(request, f'Недостаточно сырья: {ing.id_syrya.name} (нужно {needed}, есть {ing.id_syrya.quantity})')
                        return redirect('proizvodstvo_create')
                
                # 2. Списание сырья
                total_cost = 0
                for ing in ingredients:
                    needed = ing.quantity * quantity
                    # Пропорциональное списание суммы сырья
                    cost_per_unit = ing.id_syrya.amount / ing.id_syrya.quantity if ing.id_syrya.quantity > 0 else 0
                    ing.id_syrya.quantity -= needed
                    ing.id_syrya.amount -= cost_per_unit * needed
                    ing.id_syrya.save()
                    total_cost += cost_per_unit * needed
                
                # 3. Увеличение готовой продукции
                prod = GotovayaProdukcia.objects.get(id=produkcia_id)
                prod.quantity += quantity
                prod.amount += total_cost
                prod.save()
                
                # 4. Запись транзакции
                ProizvodstvoProdukcii.objects.create(
                    id_produkcii_id=produkcia_id,
                    quantity=quantity,
                    date=timezone.now(),
                    id_sotrudnika_id=sotrudnik_id
                )
                
                messages.success(request, f'Производство {quantity} ед. успешно завершено!')
                return redirect('proizvodstvo_list')
                
        except Exception as e:
            messages.error(request, f'Ошибка производства: {str(e)}')
            
    produkcia = GotovayaProdukcia.objects.all()
    sotrudniki = Sotrudniki.objects.all()
    return render(request, 'core/proizvodstvo_form.html', {
        'produkcia': produkcia,
        'sotrudniki': sotrudniki
    })

def prodazha_list(request):
    prodazhi = ProdazhaProdukcii.objects.select_related('id_produkcii', 'id_sotrudnika').all().order_by('-date')
    return render(request, 'core/prodazha_list.html', {'prodazhi': prodazhi})

def prodazha_create(request):
    if request.method == 'POST':
        produkcia_id = request.POST.get('produkcia')
        quantity = float(request.POST.get('quantity'))
        price = float(request.POST.get('price')) # Цена продажи
        sotrudnik_id = request.POST.get('sotrudnik')
        
        try:
            with transaction.atomic():
                # Проверка должности
                emp = Sotrudniki.objects.select_related('id_dolzhnosti').get(id=sotrudnik_id)
                role_name = emp.id_dolzhnosti.name.lower()
                if 'продавец' not in role_name and 'директор' not in role_name:
                    messages.error(request, f'Отказано в доступе. Должность "{emp.id_dolzhnosti.name}" не позволяет оформлять продажи!')
                    return redirect('prodazha_create')
                
                prod = GotovayaProdukcia.objects.get(id=produkcia_id)
                if prod.quantity < quantity:
                    messages.error(request, 'Недостаточно продукции на складе!')
                    return redirect('prodazha_create')
                
                # 1. Списание продукции
                cost_per_unit = prod.amount / prod.quantity if prod.quantity > 0 else 0
                prod.quantity -= quantity
                prod.amount -= cost_per_unit * quantity
                prod.save()
                
                # 2. Пополнение бюджета (выручка)
                revenue = quantity * price
                budget = Budget.objects.first()
                budget.amount += revenue
                budget.save()
                
                # 3. Запись транзакции
                ProdazhaProdukcii.objects.create(
                    id_produkcii_id=produkcia_id,
                    quantity=quantity,
                    amount=revenue,
                    date=timezone.now(),
                    id_sotrudnika_id=sotrudnik_id
                )
                
                messages.success(request, f'Продажа на сумму {revenue} сом оформлена!')
                return redirect('prodazha_list')
                
        except Exception as e:
            messages.error(request, f'Ошибка продажи: {str(e)}')
            
    produkcia = GotovayaProdukcia.objects.all()
    sotrudniki = Sotrudniki.objects.all()
    return render(request, 'core/prodazha_form.html', {
        'produkcia': produkcia,
        'sotrudniki': sotrudniki
    })

def zarplata_list(request):
    sotrudniki = Sotrudniki.objects.select_related('id_dolzhnosti').all()
    budget = Budget.objects.first()
    return render(request, 'core/zarplata_list.html', {
        'sotrudniki': sotrudniki,
        'budget': budget
    })

def zarplata_pay(request, emp_id):
    try:
        with transaction.atomic():
            emp = Sotrudniki.objects.get(id=emp_id)
            budget = Budget.objects.first()
            
            if budget.amount < emp.salary:
                messages.error(request, 'Недостаточно средств в бюджете для выплаты зарплаты!')
            else:
                budget.amount -= emp.salary
                budget.save()
                messages.success(request, f'Зарплата сотруднику {emp.fio} ({emp.salary} сом) выплачена!')
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')
    return redirect('zarplata_list')

def kredity_form(request):
    active_kredits = Kredit.objects.filter(is_paid=False)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'take':
            if active_kredits.count() >= 3:
                messages.error(request, 'Вы не можете взять более 3-х активных кредитов!')
                return redirect('kredity_form')
            
            amount = float(request.POST.get('amount'))
            try:
                with transaction.atomic():
                    budget = Budget.objects.first()
                    budget.amount += amount
                    budget.save()
                    Kredit.objects.create(amount=amount)
                    messages.success(request, f'Кредит на сумму {amount} сом успешно получен и зачислен в бюджет!')
                return redirect('kredity_form')
            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')
                
        elif action == 'pay':
            kredit_id = request.POST.get('kredit_id')
            try:
                with transaction.atomic():
                    kredit = Kredit.objects.get(id=kredit_id, is_paid=False)
                    budget = Budget.objects.first()
                    if budget.amount < kredit.amount:
                        messages.error(request, 'Недостаточно средств в бюджете для погашения кредита!')
                    else:
                        budget.amount -= kredit.amount
                        budget.save()
                        kredit.is_paid = True
                        kredit.save()
                        messages.success(request, f'Кредит на сумму {kredit.amount} сом успешно погашен!')
                return redirect('kredity_form')
            except Exception as e:
                messages.error(request, f'Ошибка: {str(e)}')
                
    return render(request, 'core/kredity_form.html', {'active_kredits': active_kredits})

def reports_dashboard(request):
    budget = Budget.objects.first()
    syrie = Syrie.objects.all()
    produkcia = GotovayaProdukcia.objects.all()
    
    # Financial Analytics
    total_expenses = ZakupkaSyrya.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_revenue = ProdazhaProdukcii.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    profit = total_revenue - total_expenses
    
    # Extra reports (Salary, Debt, Inventory)
    total_salary = Sotrudniki.objects.aggregate(Sum('salary'))['salary__sum'] or 0
    total_debt = Kredit.objects.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
    inventory_syrie = Syrie.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    inventory_gotovaya = GotovayaProdukcia.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_inventory = inventory_syrie + inventory_gotovaya
    
    # Simple analytics
    total_zakupok = ZakupkaSyrya.objects.count()
    total_proizvodstvo = ProizvodstvoProdukcii.objects.count()
    total_prodazh = ProdazhaProdukcii.objects.count()
    
    # Recent operations
    recent_purchases = list(ZakupkaSyrya.objects.select_related('id_syrya', 'id_sotrudnika').all().order_by('-date')[:10])
    recent_sales = list(ProdazhaProdukcii.objects.select_related('id_produkcii', 'id_sotrudnika').all().order_by('-date')[:10])
    
    operations = []
    for p in recent_purchases:
        operations.append({
            'type': 'Закупка',
            'item': p.id_syrya.name,
            'amount': p.amount,
            'date': p.date,
            'employee': p.id_sotrudnika.fio,
            'is_income': False
        })
    for s in recent_sales:
        operations.append({
            'type': 'Продажа',
            'item': s.id_produkcii.name,
            'amount': s.amount,
            'date': s.date,
            'employee': s.id_sotrudnika.fio,
            'is_income': True
        })
    operations.sort(key=lambda x: x['date'], reverse=True)
    operations = operations[:10]
    
    return render(request, 'core/reports.html', {
        'budget': budget,
        'syrie': syrie,
        'produkcia': produkcia,
        'operations': operations,
        'financials': {
            'expenses': total_expenses,
            'revenue': total_revenue,
            'profit': profit,
            'expenses_str': f"{total_expenses:.2f}",
            'revenue_str': f"{total_revenue:.2f}",
            'profit_str': f"{profit:.2f}",
            'salary': total_salary,
            'debt': total_debt,
            'inventory': total_inventory,
            'salary_str': f"{total_salary:.2f}",
            'debt_str': f"{total_debt:.2f}",
            'inventory_str': f"{total_inventory:.2f}"
        },
        'stats': {
            'zakupki': total_zakupok,
            'proizvodstvo': total_proizvodstvo,
            'prodazhi': total_prodazh
        }
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect('zayavki_list')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались! Можете подавать заявки.')
            return redirect('zayavki_list')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def zayavki_list(request):
    if request.user.is_staff:
        zayavki = ZayavkiNaProizvodstvo.objects.select_related('id_produkcii').all().order_by('-created_at')
    else:
        zayavki = ZayavkiNaProizvodstvo.objects.select_related('id_produkcii').filter(
            applicant_fio=request.user.username
        ).order_by('-created_at')
    return render(request, 'core/zayavki_list.html', {'zayavki': zayavki})

@login_required
def zayavki_create(request):
    if request.method == 'POST':
        produkcia_id = request.POST.get('produkcia')
        quantity = float(request.POST.get('quantity'))
        applicant_fio = request.user.username

        try:
            zayavka = ZayavkiNaProizvodstvo.objects.create(
                id_produkcii_id=produkcia_id,
                quantity=quantity,
                applicant_fio=applicant_fio,
                status='Создана'
            )
            messages.info(request, 'Заявка создана. Система запускает обработку...')
            success, msg = process_production_request_pipeline(zayavka)
            if success:
                messages.success(request, f'Заявка выполнена: {msg}')
            else:
                messages.error(request, f'Заявка не выполнена: {msg}')
            return redirect('zayavki_list')
        except Exception as e:
            messages.error(request, f'Ошибка: {str(e)}')

    produkcia = GotovayaProdukcia.objects.all()

    catalog = []
    for prod in produkcia:
        ingredients = Ingredienty.objects.filter(id_produkcii=prod).select_related('id_syrya', 'id_syrya__id_edizm')
        recipe = []
        cost = 0
        for ing in ingredients:
            raw = ing.id_syrya
            price_per_unit = raw.amount / raw.quantity if raw.quantity > 0 else 0
            edizm = raw.id_edizm.name if raw.id_edizm else 'ед.'
            recipe.append(f"{raw.name} ({ing.quantity} {edizm} по {price_per_unit:.2f} сом/{edizm})")
            cost += price_per_unit * ing.quantity

        catalog.append({
            'name': prod.name,
            'recipe': ", ".join(recipe) if recipe else "Нет рецепта",
            'cost': round(cost, 2),
            'price': round(cost * 1.30, 2),
        })

    return render(request, 'core/zayavki_form.html', {
        'produkcia': produkcia,
        'catalog': catalog
    })

def process_production_request_pipeline(zayavka):
    try:
        sotrudnik = Sotrudniki.objects.first()
        sotrudnik_id = sotrudnik.id if sotrudnik else None

        with transaction.atomic():
            zayavka.status = 'На проверке наличия сырья'
            zayavka.save()
            
            ingredients = Ingredienty.objects.filter(id_produkcii=zayavka.id_produkcii)
            total_missing_cost = 0
            missing_materials = []
            
            for ing in ingredients:
                needed = ing.quantity * zayavka.quantity
                if ing.id_syrya.quantity < needed:
                    missing = needed - ing.id_syrya.quantity
                    cost_per_unit = ing.id_syrya.amount / ing.id_syrya.quantity if ing.id_syrya.quantity > 0 else 1.0
                    missing_cost = missing * cost_per_unit
                    missing_materials.append({
                        'syrie': ing.id_syrya,
                        'qty': missing,
                        'cost': missing_cost
                    })
                    total_missing_cost += missing_cost

            if missing_materials:
                zayavka.status = 'На процессе закупки сырья'
                zayavka.save()
                
                budget = Budget.objects.first()
                if not budget or budget.amount < total_missing_cost:
                    zayavka.status = 'Ошибка'
                    zayavka.rejection_reason = 'Недостаточно средств в бюджете для закупки'
                    zayavka.save()
                    return False, "Недостаточно бюджета для закупки недостающего сырья."
                
                budget.amount -= total_missing_cost
                budget.save()
                
                for mm in missing_materials:
                    syrie = mm['syrie']
                    syrie.quantity += mm['qty']
                    syrie.amount += mm['cost']
                    syrie.save()
                    if sotrudnik_id:
                        ZakupkaSyrya.objects.create(
                            id_syrya=syrie, quantity=mm['qty'],
                            amount=mm['cost'], date=timezone.now(),
                            id_sotrudnika_id=sotrudnik_id
                        )
            
            zayavka.status = 'На процессе производства'
            zayavka.save()
            
            total_cost = 0
            for ing in ingredients:
                needed = ing.quantity * zayavka.quantity
                cost_per_unit = ing.id_syrya.amount / ing.id_syrya.quantity if ing.id_syrya.quantity > 0 else 0
                ing.id_syrya.quantity -= needed
                ing.id_syrya.amount -= cost_per_unit * needed
                ing.id_syrya.save()
                total_cost += cost_per_unit * needed
                
            prod = zayavka.id_produkcii
            prod.quantity += zayavka.quantity
            prod.amount += total_cost
            prod.save()
            
            if sotrudnik_id:
                ProizvodstvoProdukcii.objects.create(
                    id_produkcii=zayavka.id_produkcii, quantity=zayavka.quantity,
                    date=timezone.now(), id_sotrudnika_id=sotrudnik_id
                )
            
            zayavka.status = 'На процессе продажи'
            zayavka.save()
            
            cost_per_unit_prod = prod.amount / prod.quantity if prod.quantity > 0 else 0
            sales_price = cost_per_unit_prod * 1.30 * zayavka.quantity
            
            prod.quantity -= zayavka.quantity
            prod.amount -= cost_per_unit_prod * zayavka.quantity
            prod.save()
            
            budget = Budget.objects.first()
            if budget:
                budget.amount += sales_price
                budget.save()
            
            if sotrudnik_id:
                ProdazhaProdukcii.objects.create(
                    id_produkcii=zayavka.id_produkcii, quantity=zayavka.quantity,
                    amount=sales_price, date=timezone.now(),
                    id_sotrudnika_id=sotrudnik_id
                )
            
            zayavka.status = 'Выполнена'
            zayavka.rejection_reason = None
            zayavka.save()
            return True, "Конвейер успешно завершен (Закупка -> Производство -> Продажа)."
    except Exception as e:
        zayavka.status = 'Ошибка'
        zayavka.rejection_reason = str(e)
        zayavka.save()
        return False, f"Ошибка алгоритма: {str(e)}"

@login_required
def zayavka_process(request, zayavka_id):
    try:
        zayavka = ZayavkiNaProizvodstvo.objects.get(id=zayavka_id)
        is_owner = zayavka.applicant_fio == request.user.username
        if not request.user.is_staff and not is_owner:
            messages.error(request, 'У вас нет доступа к этой заявке.')
            return redirect('zayavki_list')

        if zayavka.status in ['Создана', 'Ошибка']:
            success, msg = process_production_request_pipeline(zayavka)
            if success:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        else:
            messages.info(request, 'Эта заявка уже обработана или в процессе.')
    except Exception as e:
        messages.error(request, f'Критическая ошибка: {str(e)}')
    return redirect('zayavki_list')
