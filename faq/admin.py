from django.contrib import admin
from .models import Question
from django.utils.html import format_html

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'short_content', 'position', 'created_at']
    list_editable = ['position']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    ordering = ['position']
    actions = ['move_up', 'move_down']
    
    fieldsets = (
        ('Управление видимостью', {
            'fields': (
                'position',
            ),
            'classes': ('wide',),
            'description': 'Позиция определяет порядок отображения вопроса на сайте (чем меньше число, тем выше вопрос)'
        }),
        ('Основное', {
            'fields': (
                'title',
                'content',
            ),
            'classes': ('wide',),
            'description': 'Используйте понятные заголовки и четкие ответы. Можно использовать HTML-форматирование в ответе.'
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def short_content(self, obj):
        """Возвращает сокращенную версию контента с форматированием"""
        content = obj.content
        # Удаляем HTML-теги для отображения в списке
        content = content.replace('<p>', '').replace('</p>', ' ').replace('<br>', ' ')
        if len(content) > 100:
            return format_html('<span title="{}">{}</span>', 
                             content, 
                             f"{content[:100]}...")
        return format_html('<span title="{}">{}</span>', 
                         content, 
                         content)
    short_content.short_description = 'Ответ'
    
    def move_up(self, request, queryset):
        """Перемещает выбранные вопросы выше по списку"""
        for question in queryset:
            prev_question = Question.objects.filter(
                position__lt=question.position
            ).order_by('-position').first()
            
            if prev_question:
                # Меняем позиции местами
                prev_position = prev_question.position
                prev_question.position = question.position
                question.position = prev_position
                
                prev_question.save()
                question.save()
    move_up.short_description = "Переместить выше"
    
    def move_down(self, request, queryset):
        """Перемещает выбранные вопросы ниже по списку"""
        for question in queryset:
            next_question = Question.objects.filter(
                position__gt=question.position
            ).order_by('position').first()
            
            if next_question:
                # Меняем позиции местами
                next_position = next_question.position
                next_question.position = question.position
                question.position = next_position
                
                next_question.save()
                question.save()
    move_down.short_description = "Переместить ниже"
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливает позицию для нового вопроса"""
        if not obj.pk and not obj.position:  # Если это новый объект и позиция не установлена
            last_position = Question.objects.order_by('-position').first()
            obj.position = (last_position.position + 1) if last_position else 0
        super().save_model(request, obj, form, change)
