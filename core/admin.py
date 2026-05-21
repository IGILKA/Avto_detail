from django.contrib import admin
from .models import ZayavkiNaProizvodstvo

@admin.register(ZayavkiNaProizvodstvo)
class ZayavkiNaProizvodstvoAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'applicant_fio', 'id_produkcii', 'quantity', 'created_at', 'updated_at')
    list_filter = ('status', 'id_produkcii')
    actions = ['check_materials_action']

    @admin.action(description='Проверить наличие сырья для выбранных заявок')
    def check_materials_action(self, request, queryset):
        for zayavka in queryset:
            zayavka.check_raw_materials()
        self.message_user(request, "Проверка сырья завершена для выбранных заявок.")
