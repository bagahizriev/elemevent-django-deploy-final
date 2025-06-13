from django.contrib import admin
from .models import Banner
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils.html import format_html
import uuid
import os
import shutil
from django.conf import settings

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['preview_image', 'link', 'position', 'get_colored_status']
    list_filter = ['is_active', 'created_at']
    list_editable = ['position']
    readonly_fields = ['created_at', 'updated_at', 'preview_image_large']
    search_fields = ['link']
    list_per_page = 10
    ordering = ['position']
    actions = ['duplicate_banner', 'activate_banners', 'deactivate_banners']
    
    fieldsets = (
        ('Управление видимостью', {
            'fields': (
                'is_active',
                'position',
            ),
            'classes': ('wide',),
            'description': 'Позиция определяет порядок отображения баннеров на сайте (чем меньше число, тем выше баннер)'
        }),
        ('Основное', {
            'fields': (
                'link',
                ('cover', 'preview_image_large'),
            ),
            'classes': ('wide',),
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_image(self, obj):
        """Показывает маленькое превью изображения в списке"""
        if obj.cover:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.cover.url)
        return "Нет изображения"
    preview_image.short_description = 'Превью'

    def preview_image_large(self, obj):
        """Показывает большое превью изображения в форме редактирования"""
        if obj.cover:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.cover.url)
        return "Нет изображения"
    preview_image_large.short_description = 'Предпросмотр баннера'
    
    def activate_banners(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} баннеров')
    activate_banners.short_description = "Активировать выбранные баннеры"
    
    def deactivate_banners(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} баннеров')
    deactivate_banners.short_description = "Деактивировать выбранные баннеры"
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливает позицию для нового баннера"""
        if not obj.pk and not obj.position:  # Если это новый объект и позиция не установлена
            last_position = Banner.objects.order_by('-position').first()
            obj.position = (last_position.position + 1) if last_position else 0
        super().save_model(request, obj, form, change)
    
    def duplicate_banner(self, request, queryset):
        """Действие для дублирования выбранных баннеров"""
        for banner in queryset:
            # Запоминаем путь к изображению
            cover_path = None
            
            if banner.cover and hasattr(banner.cover, 'path'):
                cover_path = banner.cover.path
            
            # Создаем копию баннера
            banner.pk = None
            
            # Временно очищаем поле изображения
            original_cover = banner.cover
            banner.cover = None
            banner.is_active = False  # Новая копия всегда неактивна
            
            # Сохраняем новый баннер
            banner.save()
            
            # Копируем изображение
            if cover_path and os.path.exists(cover_path):
                self._copy_image(cover_path, banner)
            
        messages.success(request, f"Успешно создано {queryset.count()} копий баннеров")
    duplicate_banner.short_description = "Дублировать выбранные баннеры"
    
    def _copy_image(self, source_path, banner):
        filename, ext = os.path.splitext(os.path.basename(source_path))
        new_filename = f"{uuid.uuid4().hex}{ext}"
        new_relative_path = os.path.join('banners', new_filename)
        new_full_path = os.path.join(settings.MEDIA_ROOT, 'banners', new_filename)
        
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        shutil.copy2(source_path, new_full_path)
        
        banner.cover = new_relative_path
        banner.save()

    def get_colored_status(self, obj):
        """Отображает статус баннера с соответствующим цветом"""
        if obj.is_active:
            return format_html('<span style="color: #28a745;">Активно</span>')
        return format_html('<span style="color: #dc3545;">Неактивно</span>')
    get_colored_status.short_description = 'Статус'
