from django.contrib import admin
from .models import SiteInfo
from django.contrib.admin import AdminSite

# Настройка общего вида админки
admin.site.site_header = "ElemEvent Админ-панель"
admin.site.site_title = "ElemEvent"
admin.site.index_title = "Управление сайтом"

@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('company_name', 'email'),
            'classes': ('wide',)
        }),
        ('Социальные сети', {
            'fields': ('vk_link', 'telegram_link'),
            'classes': ('wide',)
        }),
        ('Юридическая информация', {
            'fields': ('company_details', 'privacy_policy', 'terms_of_service'),
            'classes': ('wide',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Запрещаем создание новых записей, если уже есть хотя бы одна
        return not SiteInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление записей
        return False
