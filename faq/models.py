from django.db import models

# Create your models here.

class Question(models.Model):
    """Модель вопроса для FAQ (часто задаваемые вопросы)"""
    title = models.CharField(max_length=255, verbose_name="Вопрос")
    content = models.TextField(verbose_name="Ответ")
    position = models.IntegerField(default=0, blank=True, verbose_name="Позиция")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['position']
    
    def __str__(self):
        return self.title
