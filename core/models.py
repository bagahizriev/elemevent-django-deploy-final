from django.db import models
import json
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os

class JSONList(models.Field):
    """Кастомное поле для хранения списка строк в формате JSON"""
    description = "Список строк в формате JSON"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def db_type(self, connection):
        return 'text'
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        return json.loads(value)
    
    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return json.loads(value)
    
    def get_prep_value(self, value):
        if value is None:
            return None
        return json.dumps(value)
    
    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

class SiteInfo(models.Model):
    """Модель информации о сайте"""
    # Логотип удален, так как должен обновляться вручную администратором сервера
    
    # Реквизиты
    company_name = models.CharField(max_length=255, verbose_name="Название компании", default="Project")
    email = models.EmailField(verbose_name="Email", default="info@project.ru")
    vk_link = models.URLField(verbose_name="Ссылка на ВКонтакте", blank=True, null=True)
    telegram_link = models.URLField(verbose_name="Ссылка на Telegram", blank=True, null=True)
    company_details = models.TextField(verbose_name="Детали компании", blank=True, null=True, help_text="Введите каждый абзац с новой строки")
    
    # Политика конфиденциальности
    privacy_policy = models.TextField(verbose_name="Политика конфиденциальности", blank=True, null=True)
    
    # Пользовательское соглашение
    terms_of_service = models.TextField(verbose_name="Пользовательское соглашение", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return self.company_name
    
    def get_company_details_list(self):
        """Преобразует текстовое поле company_details в список для шаблона"""
        if not self.company_details:
            return []
        return self.company_details.strip().split('\n')
    
    def get_privacy_policy_list(self):
        """Преобразует текстовое поле privacy_policy в список для шаблона"""
        if not self.privacy_policy:
            return []
        return self.privacy_policy.strip().split('\n')
    
    def get_terms_of_service_list(self):
        """Преобразует текстовое поле terms_of_service в список для шаблона"""
        if not self.terms_of_service:
            return []
        return self.terms_of_service.strip().split('\n')
    
    class Meta:
        verbose_name = "Информация о сайте"
        verbose_name_plural = "Информация о сайте"

# Удалены сигналы для обработки изображений, так как поля logo больше нет
