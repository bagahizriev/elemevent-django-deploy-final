from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import uuid
import pytz
import os
from datetime import datetime, timedelta

def get_random_image_path(instance, filename):
    """Генерирует случайное имя файла, сохраняя расширение оригинального файла"""
    ext = filename.split('.')[-1]
    random_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Определяем тип изображения по имени поля
    field_name = instance._meta.get_field(instance._current_image_field).name
    if field_name == 'poster':
        return os.path.join('events/cards', random_filename)
    return os.path.join('events/covers', random_filename)

class City(models.Model):
    """Модель города с указанием часового пояса"""
    name = models.CharField(max_length=100, verbose_name="Название")
    timezone = models.CharField(max_length=50, default="Europe/Moscow", verbose_name="Часовой пояс")
    
    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class EventType(models.Model):
    """Модель типа мероприятия"""
    name = models.CharField(max_length=100, verbose_name="Название")
    
    class Meta:
        verbose_name = "Тип мероприятия"
        verbose_name_plural = "Типы мероприятий"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class AgeRestriction(models.Model):
    """Модель возрастного ограничения"""
    name = models.CharField(max_length=50, verbose_name="Название")
    
    class Meta:
        verbose_name = "Возрастное ограничение"
        verbose_name_plural = "Возрастные ограничения"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class EventStatus(models.TextChoices):
    """Статусы мероприятия"""
    DRAFT = 'DRAFT', 'Черновик'
    ACTIVE = 'ACTIVE', 'Активно'
    STOP = 'STOP', 'Приостановлено'
    CANCEL = 'CANCEL', 'Отменено'

class TicketSystemType(models.TextChoices):
    """Типы билетных систем"""
    DIRECT = 'DIRECT', 'Прямая ссылка'
    TICKETSCLOUD = 'TICKETSCLOUD', 'TicketsCloud'
    RADARIO = 'RADARIO', 'Radario'

class Event(models.Model):
    """Модель мероприятия"""
    ARCHIVE_DELAY_CHOICES = [
        (0, '0 часов'),
        (1, '1 час'),
        (2, '2 часа'),
        (3, '3 часа'),
        (6, '6 часов'),
        (12, '12 часов'),
        (24, '24 часа'),
        (36, '36 часов'),
    ]
    
    def _get_upload_path_for_poster(self, filename):
        self._current_image_field = 'poster'
        return get_random_image_path(self, filename)
    
    def _get_upload_path_for_cover(self, filename):
        self._current_image_field = 'cover'
        return get_random_image_path(self, filename)
    
    poster = models.ImageField(upload_to=_get_upload_path_for_poster, verbose_name="Обложка для карточки")
    cover = models.ImageField(upload_to=_get_upload_path_for_cover, verbose_name="Обложка для страницы")
    title = models.CharField(max_length=255, verbose_name="Название")
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name="Город")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время")
    venue = models.CharField(max_length=255, verbose_name="Площадка")
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT, null=True, verbose_name="Тип мероприятия")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    age_restriction = models.ForeignKey(AgeRestriction, on_delete=models.PROTECT, null=True, verbose_name="Возрастное ограничение")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    
    # Новые поля для билетных систем
    ticket_system = models.CharField(
        max_length=20,
        choices=TicketSystemType.choices,
        default=TicketSystemType.DIRECT,
        verbose_name="Система продажи билетов"
    )
    ticket_link = models.URLField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Прямая ссылка на билеты",
        help_text="Используется только при выборе типа 'Прямая ссылка'"
    )
    ticketscloud_event_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID события TicketsCloud",
        help_text="Например: 6821dfc8b521c11bd5e8e245"
    )
    ticketscloud_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Токен TicketsCloud",
        help_text="Например: eyJhbGciOiJIUzI1NiIsImlzcyI6..."
    )
    radario_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID события Radario",
        help_text="Введите только цифровой ID события (например: 123456)"
    )
    
    vk_link = models.URLField(max_length=255, blank=True, null=True, verbose_name="Ссылка на встречу ВК")
    archive_delay = models.IntegerField(choices=ARCHIVE_DELAY_CHOICES, default=3, verbose_name="Время до архивирования (часов)")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    status = models.CharField(
        max_length=10,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT,
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.title} - {self.city.name} ({self.date})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('event_detail', args=[self.slug])
        
    def is_past(self):
        """Проверяет, прошло ли мероприятие на текущий момент с учетом времени до архивирования"""
        try:
            # Получаем текущее время по UTC
            now = timezone.now()
            
            # Получаем часовой пояс мероприятия
            event_timezone = pytz.timezone(self.city.timezone)
            
            # Создаем datetime объект из даты и времени мероприятия
            event_datetime = datetime.combine(self.date, self.time)
            
            # Локализуем время мероприятия в его часовом поясе
            event_datetime = event_timezone.localize(event_datetime)
            
            # Добавляем дополнительное время до архивирования
            archive_datetime = event_datetime + timedelta(hours=self.archive_delay)
            
            # Сравниваем с текущим временем
            return archive_datetime < now
        except Exception:
            # В случае ошибок при работе с часовыми поясами возвращаем False
            return False

    def is_visible(self):
        """Проверяет, должно ли мероприятие отображаться в списках"""
        return self.status == EventStatus.ACTIVE

    def is_cancelled(self):
        """Проверяет, отменено ли мероприятие"""
        return self.status == EventStatus.CANCEL

    def is_stopped(self):
        """Проверяет, приостановлено ли мероприятие"""
        return self.status == EventStatus.STOP

    def delete_old_image(self, field_name):
        """Удаляет старое изображение, если оно было заменено"""
        try:
            # Получаем путь к старому файлу
            old_instance = Event.objects.get(pk=self.pk)
            old_file = getattr(old_instance, field_name)
            if old_file and old_file != getattr(self, field_name):
                if os.path.isfile(old_file.path):
                    os.remove(old_file.path)
        except (Event.DoesNotExist, ValueError, FileNotFoundError):
            # Если объект новый или файл не найден, ничего не делаем
            pass

# Сигнал для обработки удаления старых изображений при обновлении
@receiver(pre_save, sender=Event)
def delete_old_images_on_update(sender, instance, **kwargs):
    """Обработчик сигнала, который удаляет старые изображения при обновлении события"""
    if instance.pk:  # Если объект уже существует (не создание нового)
        instance.delete_old_image('poster')
        instance.delete_old_image('cover')

# Сигнал для обработки удаления файлов при удалении объекта
@receiver(post_delete, sender=Event)
def delete_files_on_delete(sender, instance, **kwargs):
    """Обработчик сигнала, который удаляет файлы при удалении события"""
    # Удаляем файлы постера, если он существует
    if instance.poster:
        if os.path.isfile(instance.poster.path):
            os.remove(instance.poster.path)
    
    # Удаляем файлы обложки, если она существует
    if instance.cover:
        if os.path.isfile(instance.cover.path):
            os.remove(instance.cover.path)

class EventPush(models.Model):
    event = models.OneToOneField('Event', on_delete=models.CASCADE, related_name='push')
    content = models.TextField(verbose_name='Содержимое пуша', help_text='Поддерживается HTML разметка')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Пуш мероприятия'
        verbose_name_plural = 'Пуши мероприятий'

    def __str__(self):
        return f'Пуш для {self.event}'

class EventAdvertising(models.Model):
    event = models.OneToOneField('Event', on_delete=models.CASCADE, related_name='advertising')
    is_active = models.BooleanField(default=False, verbose_name='Активно')
    token = models.CharField(max_length=100, verbose_name='ERID токен')
    advertiser_name = models.CharField(max_length=255, verbose_name='Наименование рекламодателя')
    advertiser_inn = models.CharField(max_length=12, verbose_name='ИНН рекламодателя')
    advertiser_ogrn = models.CharField(max_length=15, verbose_name='ОГРН рекламодателя', blank=True, null=True)
    additional_info = models.TextField(verbose_name='Дополнительная информация', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Рекламная информация'
        verbose_name_plural = 'Рекламная информация'

    def __str__(self):
        return f'Реклама для {self.event}'
