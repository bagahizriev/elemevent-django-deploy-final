from django.shortcuts import render
from .models import Question

def faq_list(request):
    """Страница FAQ (часто задаваемые вопросы)"""
    # Получаем все вопросы, отсортированные по позиции
    questions = Question.objects.all().order_by('position')
    
    context = {
        'questions': questions,
        'title': 'Часто задаваемые вопросы',
    }
    return render(request, 'faq/faq_list.html', context)
