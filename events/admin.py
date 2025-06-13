from django.contrib import admin
from .models import Event, City, EventType, AgeRestriction, EventStatus, EventPush, EventAdvertising
from django.contrib import messages
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.db.models import ProtectedError
from django.utils import timezone
import uuid
import os
import shutil
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'timezone', 'is_used']
    search_fields = ['name']
    list_filter = ['timezone']
    
    def is_used(self, obj):
        is_used = obj.event_set.exists()
        return format_html(
            '<span style="color: {}">&#x{}</span>',
            '#28a745' if is_used else '#dc3545',
            '2713' if is_used else '2717'
        )
    is_used.short_description = 'Используется'
    
    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ProtectedError as e:
            self.message_user(request, str(e.args[0]), messages.ERROR)
            return False
    
    def delete_queryset(self, request, queryset):
        try:
            queryset.delete()
        except ProtectedError as e:
            self.message_user(request, str(e.args[0]), messages.ERROR)

@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_used']
    search_fields = ['name']
    
    def is_used(self, obj):
        is_used = obj.event_set.exists()
        return format_html(
            '<span style="color: {}">&#x{}</span>',
            '#28a745' if is_used else '#dc3545',
            '2713' if is_used else '2717'
        )
    is_used.short_description = 'Используется'
    
    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ProtectedError as e:
            self.message_user(request, str(e.args[0]), messages.ERROR)
            return False
    
    def delete_queryset(self, request, queryset):
        try:
            queryset.delete()
        except ProtectedError as e:
            self.message_user(request, str(e.args[0]), messages.ERROR)

@admin.register(AgeRestriction)
class AgeRestrictionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_used']
    search_fields = ['name']
    
    def is_used(self, obj):
        is_used = obj.event_set.exists()
        return format_html(
            '<span style="color: {}">&#x{}</span>',
            '#28a745' if is_used else '#dc3545',
            '2713' if is_used else '2717'
        )
    is_used.short_description = 'Используется'
    
    def delete_model(self, request, obj):
        try:
            obj.delete()
        except ProtectedError as e:
            self.message_user(request, str(e.args[0]), messages.ERROR)
            return False
    
    def delete_queryset(self, request, queryset):
        try:
            queryset.delete()
        except ProtectedError as e:
            self.message_user(request, str(e.args[0]), messages.ERROR)

class EventPushInline(admin.StackedInline):
    model = EventPush
    can_delete = True
    extra = 0

class EventAdvertisingInline(admin.StackedInline):
    model = EventAdvertising
    can_delete = True
    extra = 0

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'admin/js/slug_warning.js',
            'admin/js/ticket_system_fields.js',  # Добавим новый файл для управления видимостью полей
        )

    list_display = ['preview_poster_small', 'title', 'city', 'date', 'venue', 'get_colored_status', 'get_section', 'get_ticket_system']
    list_filter = ['status', 'city', 'date', 'event_type', 'age_restriction', 'ticket_system']
    search_fields = ['title', 'venue', 'description', 'city__name']
    autocomplete_fields = ['city', 'event_type', 'age_restriction']
    prepopulated_fields = {}  # Отключаем автоматическое заполнение slug
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'preview_poster', 
        'preview_cover',
        'preview_poster_small'
    ]
    date_hierarchy = 'date'
    list_per_page = 20
    actions = ['duplicate_event', 'make_active', 'make_draft', 'stop_events', 'cancel_events']
    inlines = [EventPushInline, EventAdvertisingInline]
    
    fieldsets = (
        ('Управление видимостью', {
            'fields': (
                'status',
                'slug',
            ),
            'classes': ('wide',),
        }),
        ('Основное', {
            'fields': (
                'title',
                'city',
                'event_type',
                'age_restriction',
            ),
            'classes': ('wide',),
        }),
        ('Анонс', {
            'fields': (
                'date',
                'time',
                'archive_delay',
                'venue',
                'address',
                'description',
                ('poster', 'preview_poster'),
                ('cover', 'preview_cover'),
            ),
            'classes': ('wide',),
            'description': 'Указывайте время в часовом поясе города проведения'
        }),
        ('Билетная система', {
            'fields': (
                'ticket_system',
                'ticket_link',
                ('ticketscloud_event_id', 'ticketscloud_token'),
                'radario_key',
            ),
            'classes': ('wide',),
            'description': 'Выберите тип билетной системы и заполните соответствующие поля'
        }),
        ('Дополнительные ссылки', {
            'fields': (
                'vk_link',
            ),
            'classes': ('wide',),
        }),
        ('Системная информация', {
            'fields': (
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_section(self, obj):
        """Определяет, в каком разделе отображается мероприятие"""
        if obj.status != EventStatus.ACTIVE:
            return "Скрыто"
            
        if obj.is_past():
            return "Архив"
            
        return "Афиша"
    get_section.short_description = "Раздел"
    
    def preview_poster(self, obj):
        """Превью постера"""
        if obj.poster:
            return mark_safe(f'<img src="{obj.poster.url}" style="max-height: 200px;"/>')
        return 'Нет изображения'
    preview_poster.short_description = 'Предпросмотр постера'
    
    def preview_cover(self, obj):
        """Превью обложки"""
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
    
    def get_absolute_url(self, obj):
        """Ссылка на мероприятие на сайте"""
        if obj.pk:
            url = obj.get_absolute_url()
            return format_html(f'<a href="{url}" target="_blank">Открыть на сайте</a>')
        return '—'
    get_absolute_url.short_description = 'Ссылка на сайте'
    
    def make_active(self, request, queryset):
        updated = queryset.update(status=EventStatus.ACTIVE)
        self.message_user(request, f'Активировано {updated} мероприятий')
    make_active.short_description = "Активировать выбранные мероприятия"
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status=EventStatus.DRAFT)
        self.message_user(request, f'{updated} мероприятий переведено в черновики')
    make_draft.short_description = "Перевести выбранные мероприятия в черновики"
    
    def stop_events(self, request, queryset):
        updated = queryset.update(status=EventStatus.STOP)
        self.message_user(request, f'Приостановлено {updated} мероприятий')
    stop_events.short_description = "Приостановить выбранные мероприятия"
    
    def cancel_events(self, request, queryset):
        updated = queryset.update(status=EventStatus.CANCEL)
        self.message_user(request, f'Отменено {updated} мероприятий')
    cancel_events.short_description = "Отменить выбранные мероприятия"
    
    def duplicate_event(self, request, queryset):
        """Действие для дублирования выбранных мероприятий"""
        for event in queryset:
            # Запоминаем туры, связанные с мероприятием
            tours = list(event.tours.all())
            
            # Запоминаем пути к исходным изображениям
            poster_path = None
            cover_path = None
            
            if event.poster and hasattr(event.poster, 'path'):
                poster_path = event.poster.path
            
            if event.cover and hasattr(event.cover, 'path'):
                cover_path = event.cover.path
            
            # Создаем копию мероприятия
            event.pk = None
            
            # Временно очищаем поля изображений
            original_poster = event.poster
            original_cover = event.cover
            event.poster = None
            event.cover = None
            
            # Генерируем новый случайный slug
            unique_id = str(uuid.uuid4())[:8]
            event.slug = f"{slugify(event.title)}-{unique_id}"
            
            # Добавляем '(копия)' к названию
            event.title = f"{event.title} (копия)"
            event.status = EventStatus.DRAFT  # Новая копия всегда создается как черновик
            
            # Сохраняем новое мероприятие
            event.save()
            
            # Копируем изображения
            if poster_path and os.path.exists(poster_path):
                self._copy_image(poster_path, event, 'poster', 'events/posters')
            
            if cover_path and os.path.exists(cover_path):
                self._copy_image(cover_path, event, 'cover', 'events/covers')
            
            # Восстанавливаем связи с турами
            for tour in tours:
                tour.events.add(event)
            
        messages.success(request, f"Успешно создано {queryset.count()} копий мероприятий")
    duplicate_event.short_description = "Дублировать выбранные мероприятия"
    
    def _copy_image(self, source_path, event, field_name, target_dir):
        filename, ext = os.path.splitext(os.path.basename(source_path))
        new_filename = f"{uuid.uuid4().hex}{ext}"
        new_relative_path = os.path.join(target_dir, new_filename)
        new_full_path = os.path.join(settings.MEDIA_ROOT, target_dir, new_filename)
        
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        shutil.copy2(source_path, new_full_path)
        
        setattr(event, field_name, new_relative_path)
        event.save()

    def get_colored_status(self, obj):
        """Отображает статус мероприятия с соответствующим цветом"""
        colors = {
            EventStatus.ACTIVE: '#28a745',  # зеленый
            EventStatus.DRAFT: '#ffc107',   # желтый
            EventStatus.STOP: '#dc3545',    # красный
            EventStatus.CANCEL: '#6c757d'   # серый
        }
        status_names = {
            EventStatus.ACTIVE: 'Активно',
            EventStatus.DRAFT: 'Черновик',
            EventStatus.STOP: 'Приостановлено',
            EventStatus.CANCEL: 'Отменено'
        }
        color = colors.get(obj.status, '#000000')
        status_name = status_names.get(obj.status, obj.status)
        return format_html('<span style="color: {}">{}</span>', color, status_name)
    get_colored_status.short_description = 'Статус'

    def get_ticket_system(self, obj):
        """Отображает тип билетной системы в списке"""
        return obj.get_ticket_system_display()
    get_ticket_system.short_description = 'Билетная система'

    def get_prepopulated_fields(self, request, obj=None):
        # Если это создание нового объекта (obj=None), возвращаем prepopulated_fields
        # Если это редактирование (obj!=None), возвращаем пустой словарь
        if obj is None:
            return {"slug": ("title",)}
        return {}
