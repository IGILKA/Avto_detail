from django.db import models

class EdiniziIzmerenia(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    name = models.CharField(db_column='Наименование', max_length=50)

    class Meta:
        managed = False
        db_table = '[Производство].[ЕдиницыИзмерения]'

class Dolzhnosti(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    name = models.CharField(db_column='Должность', max_length=100)

    class Meta:
        managed = False
        db_table = '[Производство].[Должности]'

class Sotrudniki(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    fio = models.CharField(db_column='ФИО', max_length=200)
    id_dolzhnosti = models.ForeignKey(Dolzhnosti, models.DO_NOTHING, db_column='ИД_Должности')
    salary = models.FloatField(db_column='ЗаработнаяПлата')
    address = models.CharField(db_column='Адрес', max_length=300, blank=True, null=True)
    phone = models.CharField(db_column='Телефон', max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[Производство].[Сотрудники]'

class Budget(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    amount = models.FloatField(db_column='СуммаБюджета')

    class Meta:
        managed = False
        db_table = '[Производство].[Бюджет]'

class Syrie(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    name = models.CharField(db_column='Наименование', max_length=150)
    id_edizm = models.ForeignKey(EdiniziIzmerenia, models.DO_NOTHING, db_column='ИД_ЕдИзм')
    quantity = models.FloatField(db_column='Количество')
    amount = models.FloatField(db_column='Сумма')

    class Meta:
        managed = False
        db_table = '[Производство].[Сырье]'

class GotovayaProdukcia(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    name = models.CharField(db_column='Наименование', max_length=150)
    id_edizm = models.ForeignKey(EdiniziIzmerenia, models.DO_NOTHING, db_column='ИД_ЕдИзм')
    quantity = models.FloatField(db_column='Количество')
    amount = models.FloatField(db_column='Сумма')

    class Meta:
        managed = False
        db_table = '[Производство].[ГотоваяПродукция]'

class Ingredienty(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    id_produkcii = models.ForeignKey(GotovayaProdukcia, models.DO_NOTHING, db_column='ИД_Продукции')
    id_syrya = models.ForeignKey(Syrie, models.DO_NOTHING, db_column='ИД_Сырья')
    quantity = models.FloatField(db_column='Количество')

    class Meta:
        managed = False
        db_table = '[Производство].[Ингредиенты]'

class ZakupkaSyrya(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    id_syrya = models.ForeignKey(Syrie, models.DO_NOTHING, db_column='ИД_Сырья')
    quantity = models.FloatField(db_column='Количество')
    amount = models.FloatField(db_column='Сумма')
    date = models.DateTimeField(db_column='Дата')
    id_sotrudnika = models.ForeignKey(Sotrudniki, models.DO_NOTHING, db_column='ИД_Сотрудника')

    class Meta:
        managed = False
        db_table = '[Производство].[ЗакупкаСырья]'

class ProizvodstvoProdukcii(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    id_produkcii = models.ForeignKey(GotovayaProdukcia, models.DO_NOTHING, db_column='ИД_Продукции')
    quantity = models.FloatField(db_column='Количество')
    date = models.DateTimeField(db_column='Дата')
    id_sotrudnika = models.ForeignKey(Sotrudniki, models.DO_NOTHING, db_column='ИД_Сотрудника')

    class Meta:
        managed = False
        db_table = '[Производство].[ПроизводствоПродукции]'

class ProdazhaProdukcii(models.Model):
    id = models.AutoField(db_column='ИД', primary_key=True)
    id_produkcii = models.ForeignKey(GotovayaProdukcia, models.DO_NOTHING, db_column='ИД_Продукции')
    quantity = models.FloatField(db_column='Количество')
    amount = models.FloatField(db_column='Сумма')
    date = models.DateTimeField(db_column='Дата')
    id_sotrudnika = models.ForeignKey(Sotrudniki, models.DO_NOTHING, db_column='ИД_Сотрудника')

    class Meta:
        managed = False
        db_table = '[Производство].[ПродажаПродукции]'

class Kredit(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.FloatField(db_column='Сумма', verbose_name='Сумма кредита')
    is_paid = models.BooleanField(default=False, db_column='Погашен', verbose_name='Кредит погашен')
    date_taken = models.DateTimeField(auto_now_add=True, db_column='Дата_Получения', verbose_name='Дата получения')

    class Meta:
        db_table = 'Кредиты'

class ZayavkiNaProizvodstvo(models.Model):
    id = models.AutoField(primary_key=True, db_column='Идентификатор_заявки')
    created_at = models.DateTimeField(auto_now_add=True, db_column='Дата_создания', verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, db_column='Дата_последнего_обновления', verbose_name='Дата последнего обновления')
    
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('На проверке наличия сырья', 'На проверке наличия сырья'),
        ('На процессе закупки сырья', 'На процессе закупки сырья'),
        ('На процессе производства', 'На процессе производства'),
        ('На процессе продажи', 'На процессе продажи'),
        ('Выполнена', 'Выполнена'),
        ('Ошибка', 'Ошибка'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Создана', db_column='Статус', verbose_name='Статус')
    applicant_fio = models.CharField(max_length=200, db_column='ФИО_заявителя', verbose_name='ФИО заявителя')
    id_produkcii = models.ForeignKey(GotovayaProdukcia, models.DO_NOTHING, db_column='ИД_готовой_продукции', db_constraint=False, verbose_name='Идентификатор готовой продукции')
    quantity = models.FloatField(db_column='Количество', verbose_name='Количество', default=1.0)
    rejection_reason = models.TextField(blank=True, null=True, db_column='Причина_отказа', verbose_name='Причина отказа')

    class Meta:
        db_table = 'Заявки_на_производство'
        verbose_name = 'Заявка на производство'
        verbose_name_plural = 'Заявки на производство'

    def check_raw_materials(self):
        """
        Check if we have enough raw materials to produce the requested volume.
        """
        ingredients = Ingredienty.objects.filter(id_produkcii=self.id_produkcii)
        
        sufficient_materials = True
        for ingredient in ingredients:
            required_amount = ingredient.quantity * self.quantity
            raw_material = ingredient.id_syrya
            if raw_material.quantity < required_amount:
                sufficient_materials = False
                break
        
        if sufficient_materials:
            self.status = 'На процессе производства'
        else:
            self.status = 'На процессе закупки сырья'
        
        self.save()
