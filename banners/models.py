from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os
import uuid

def get_random_image_path(instance, filename):
    """Генерирует случайное имя файла, сохраняя расширение оригинального файла"""
    ext = filename.split('.')[-1]
    random_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('banners', random_filename)

class Banner(models.Model):
    """Модель баннера на главной странице"""
    cover = models.ImageField(upload_to=get_random_image_path, verbose_name="Изображение баннера")
    link = models.CharField(max_length=255, verbose_name="Ссылка")
    position = models.IntegerField(default=0, blank=True, verbose_name="Позиция")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ['position']
    
    def __str__(self):
        return f"Баннер #{self.id} ({self.position})"
        
    def delete_old_image(self, field_name):
        """Удаляет старое изображение, если оно было заменено"""
        try:
            # Получаем путь к старому файлу
            old_instance = Banner.objects.get(pk=self.pk)
            old_file = getattr(old_instance, field_name)
            if old_file and old_file != getattr(self, field_name):
                if os.path.isfile(old_file.path):
                    os.remove(old_file.path)
        except (Banner.DoesNotExist, ValueError, FileNotFoundError):
            # Если объект новый или файл не найден, ничего не делаем
            pass

# Сигнал для обработки удаления старых изображений при обновлении
@receiver(pre_save, sender=Banner)
def delete_old_images_on_update(sender, instance, **kwargs):
    """Обработчик сигнала, который удаляет старые изображения при обновлении баннера"""
    if instance.pk:  # Если объект уже существует (не создание нового)
        instance.delete_old_image('cover')

# Сигнал для обработки удаления файлов при удалении объекта
@receiver(post_delete, sender=Banner)
def delete_files_on_delete(sender, instance, **kwargs):
    """Обработчик сигнала, который удаляет файлы при удалении баннера"""
    # Удаляем файл обложки, если он существует
    if instance.cover:
        if os.path.isfile(instance.cover.path):
            os.remove(instance.cover.path)
