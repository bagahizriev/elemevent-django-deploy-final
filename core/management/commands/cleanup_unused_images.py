from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import FileField
from django.apps import apps
import os
import re


class Command(BaseCommand):
    help = 'Удаляет неиспользуемые изображения из медиа-директории'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только показывает, какие файлы будут удалены, без реального удаления',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Получаем все поля с файлами из всех моделей
        file_fields = []
        for model in apps.get_models():
            file_fields.extend([
                (f.name, model)
                for f in model._meta.fields
                if isinstance(f, FileField)
            ])
        
        # Получаем все используемые файлы
        used_files = set()
        for field_name, model in file_fields:
            for instance in model.objects.all():
                file_instance = getattr(instance, field_name)
                if file_instance and file_instance.name:
                    used_files.add(file_instance.path)
        
        # Получаем все файлы в медиа директории
        media_root = settings.MEDIA_ROOT
        all_files = []
        for root, dirs, files in os.walk(media_root):
            for file in files:
                # Игнорируем .gitignore и другие служебные файлы
                if not file.startswith('.'):
                    all_files.append(os.path.join(root, file))
        
        # Фильтруем только изображения (с расширениями jpg, jpeg, png, gif, webp, svg)
        image_files = [
            file for file in all_files 
            if re.search(r'\.(jpg|jpeg|png|gif|webp|svg)$', file.lower())
        ]
        
        # Находим неиспользуемые изображения
        unused_images = [
            file for file in image_files
            if file not in used_files
        ]
        
        # Выводим информацию
        self.stdout.write(f"Найдено изображений: {len(image_files)}")
        self.stdout.write(f"Используется изображений: {len(used_files)}")
        self.stdout.write(f"Неиспользуемых изображений: {len(unused_images)}")
        
        # Если есть неиспользуемые изображения
        if unused_images:
            if dry_run:
                self.stdout.write(self.style.WARNING("Dry-run режим. Следующие файлы будут удалены:"))
                for file in unused_images:
                    self.stdout.write(f" - {os.path.relpath(file, media_root)}")
            else:
                count = 0
                for file in unused_images:
                    try:
                        os.remove(file)
                        count += 1
                        self.stdout.write(f" - Удален файл: {os.path.relpath(file, media_root)}")
                    except OSError as e:
                        self.stdout.write(self.style.ERROR(f" - Ошибка при удалении {os.path.relpath(file, media_root)}: {e}"))
                
                self.stdout.write(self.style.SUCCESS(f"Успешно удалено {count} неиспользуемых изображений"))
        else:
            self.stdout.write(self.style.SUCCESS("Неиспользуемых изображений не найдено")) 