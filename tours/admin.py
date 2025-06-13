from django.contrib import admin
from .models import Tour, TourEvent
from django.contrib import messages
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.utils import timezone
import uuid
import os
import shutil
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class TourEventInline(admin.TabularInline):
    model = TourEvent
    extra = 1
    autocomplete_fields = ['event']
    classes = ['collapse']

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    class Media:
        js = ('admin/js/slug_warning.js',)

    list_display = ['preview_poster_small', 'title', 'get_colored_status', 'get_section']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'events__title']
    prepopulated_fields = {}  # Отключаем автоматическое заполнение slug
    readonly_fields = ['created_at', 'updated_at', 'preview_poster', 'preview_cover', 'preview_poster_small']
    inlines = [TourEventInline]
    actions = ['duplicate_tour', 'activate_tours', 'deactivate_tours']
    list_per_page = 20
    
    fieldsets = (
        ('Управление видимостью', {
            'fields': (
                'is_active',
                'slug',
            ),
            'classes': ('wide',),
        }),
        ('Основное', {
            'fields': ('title',),
            'classes': ('wide',),
        }),
        ('Медиа', {
            'fields': (
                ('poster', 'preview_poster'),
                ('cover', 'preview_cover'),
            ),
            'classes': ('wide',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_events_count(self, obj):
        return obj.events.count()
    get_events_count.short_description = 'Количество мероприятий'
    
    def get_section(self, obj):
        """Определяет раздел, в котором отображается тур"""
        if not obj.is_active:
            return "Скрыто"
            
        # Получаем активные мероприятия тура
        active_events = obj.events.filter(status='ACTIVE')
        
        # Проверяем, есть ли хотя бы одно непрошедшее мероприятие
        has_upcoming_events = False
        for event in active_events:
            if not event.is_past():
                has_upcoming_events = True
                break
        
        if has_upcoming_events:
            return "Афиша"
        return "Скрыто"
    get_section.short_description = "Раздел"
    
    def activate_tours(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} туров')
    activate_tours.short_description = "Активировать выбранные туры"
    
    def deactivate_tours(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} туров')
    deactivate_tours.short_description = "Деактивировать выбранные туры"
    
    def duplicate_tour(self, request, queryset):
        """Действие для дублирования выбранных туров"""
        for tour in queryset:
            # Запоминаем мероприятия
            events = list(tour.events.all())
            
            # Запоминаем пути к изображениям
            poster_path = None
            cover_path = None
            
            if tour.poster and hasattr(tour.poster, 'path'):
                poster_path = tour.poster.path
            
            if tour.cover and hasattr(tour.cover, 'path'):
                cover_path = tour.cover.path
            
            # Создаем копию тура
            tour.pk = None
            
            # Временно очищаем поля изображений
            original_poster = tour.poster
            original_cover = tour.cover
            tour.poster = None
            tour.cover = None
            
            # Генерируем новый slug
            unique_id = str(uuid.uuid4())[:8]
            tour.slug = f"{slugify(tour.title)}-{unique_id}"
            
            # Добавляем пометку копии
            tour.title = f"{tour.title} (копия)"
            tour.is_active = False  # Новая копия всегда неактивна
            
            # Сохраняем новый тур
            tour.save()
            
            # Копируем изображения
            if poster_path and os.path.exists(poster_path):
                self._copy_image(poster_path, tour, 'poster', 'tours/posters')
            
            if cover_path and os.path.exists(cover_path):
                self._copy_image(cover_path, tour, 'cover', 'tours/covers')
            
            # Восстанавливаем связи с мероприятиями
            for event in events:
                tour.events.add(event)
            
        messages.success(request, f"Успешно создано {queryset.count()} копий туров")
    duplicate_tour.short_description = "Дублировать выбранные туры"
    
    def _copy_image(self, source_path, tour, field_name, target_dir):
        filename, ext = os.path.splitext(os.path.basename(source_path))
        new_filename = f"{uuid.uuid4().hex}{ext}"
        new_relative_path = os.path.join(target_dir, new_filename)
        new_full_path = os.path.join(settings.MEDIA_ROOT, target_dir, new_filename)
        
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        shutil.copy2(source_path, new_full_path)
        
        setattr(tour, field_name, new_relative_path)
        tour.save()

    def preview_poster(self, obj):
        if obj.poster:
            return mark_safe(f'<img src="{obj.poster.url}" style="max-height: 200px;"/>')
        return 'Нет изображения'
    preview_poster.short_description = 'Предпросмотр постера'

    def preview_cover(self, obj):
        if obj.cover:
            return mark_safe(f'<img src="{obj.cover.url}" style="max-height: 200px;"/>')
        return 'Нет изображения'
    preview_cover.short_description = 'Предпросмотр обложки'

    def preview_poster_small(self, obj):
        """Показывает маленькое превью постера в списке"""
        if obj.poster:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.poster.url)
        return "Нет постера"
    preview_poster_small.short_description = 'Постер'

    def get_colored_status(self, obj):
        """Отображает статус тура с соответствующим цветом"""
        if obj.is_active:
            return format_html('<span style="color: #28a745;">Активно</span>')
        return format_html('<span style="color: #dc3545;">Неактивно</span>')
    get_colored_status.short_description = 'Статус'

    def get_prepopulated_fields(self, request, obj=None):
        if obj is None:
            return {"slug": ("title",)}
        return {}

@admin.register(TourEvent)
class TourEventAdmin(admin.ModelAdmin):
    list_display = ['tour', 'event', 'created_at']
    list_filter = ['tour', 'event__status']
    search_fields = ['tour__title', 'event__title']
    autocomplete_fields = ['tour', 'event']
    readonly_fields = ['created_at']
