from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from events.models import Event
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import uuid
import os

def get_random_image_path(instance, filename):
    """Генерирует случайное имя файла, сохраняя расширение оригинального файла"""
    ext = filename.split('.')[-1]
    random_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Определяем тип изображения по имени поля
    field_name = instance._meta.get_field(instance._current_image_field).name
    if field_name == 'poster':
        return os.path.join('tours/cards', random_filename)
    return os.path.join('tours/covers', random_filename)

class Tour(models.Model):
    """Модель тура"""
    def _get_upload_path_for_poster(self, filename):
        self._current_image_field = 'poster'
        return get_random_image_path(self, filename)
    
    def _get_upload_path_for_cover(self, filename):
        self._current_image_field = 'cover'
        return get_random_image_path(self, filename)
    
    title = models.CharField(max_length=255, verbose_name="Название")
    poster = models.ImageField(upload_to=_get_upload_path_for_poster, verbose_name="Обложка для карточки")
    cover = models.ImageField(upload_to=_get_upload_path_for_cover, verbose_name="Обложка для страницы")
    events = models.ManyToManyField(Event, through='TourEvent', related_name='tours', verbose_name="Мероприятия")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('tour_detail', args=[self.slug])

    def delete_old_image(self, field_name):
        """Удаляет старое изображение, если оно было заменено"""
        try:
            # Получаем путь к старому файлу
            old_instance = Tour.objects.get(pk=self.pk)
            old_file = getattr(old_instance, field_name)
            if old_file and old_file != getattr(self, field_name):
                if os.path.isfile(old_file.path):
                    os.remove(old_file.path)
        except (Tour.DoesNotExist, ValueError, FileNotFoundError):
            # Если объект новый или файл не найден, ничего не делаем
            pass

# Сигнал для обработки удаления старых изображений при обновлении
@receiver(pre_save, sender=Tour)
def delete_old_images_on_update(sender, instance, **kwargs):
    """Обработчик сигнала, который удаляет старые изображения при обновлении тура"""
    if instance.pk:  # Если объект уже существует (не создание нового)
        instance.delete_old_image('poster')
        instance.delete_old_image('cover')

# Сигнал для обработки удаления файлов при удалении объекта
@receiver(post_delete, sender=Tour)
def delete_files_on_delete(sender, instance, **kwargs):
    """Обработчик сигнала, который удаляет файлы при удалении тура"""
    # Удаляем файлы постера, если он существует
    if instance.poster:
        if os.path.isfile(instance.poster.path):
            os.remove(instance.poster.path)
    
    # Удаляем файлы обложки, если она существует
    if instance.cover:
        if os.path.isfile(instance.cover.path):
            os.remove(instance.cover.path)

class TourEvent(models.Model):
    """Модель связи тура и мероприятия"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='tour_events', verbose_name="Тур")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tour_events', verbose_name="Мероприятие")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Связь тура и мероприятия"
        verbose_name_plural = "Связи туров и мероприятий"
        unique_together = ('tour', 'event')
    
    def __str__(self):
        return f"{self.tour.title} - {self.event.title}"
