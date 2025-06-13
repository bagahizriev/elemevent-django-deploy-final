from django.shortcuts import render
from events.models import Event, City, EventType, AgeRestriction, EventStatus
from tours.models import Tour
from banners.models import Banner
from faq.models import Question
from django.utils import timezone
from django.db.models import Q
import datetime
import pytz
from django.conf import settings

def index(request):
    """Главная страница сайта"""
    # Получаем активные баннеры
    banners = Banner.objects.filter(is_active=True).order_by('position')
    
    # Получаем текущую дату и время
    now = timezone.now()
    today = now.date()
    
    # Получаем все ближайшие мероприятия без ограничения по количеству
    # Фильтруем только активные мероприятия, которые еще не прошли
    upcoming_events = []
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    
    # Проверяем каждое мероприятие
    for event in events:
        if not event.is_past():
            upcoming_events.append(event)
    
    # Получаем активные туры (увеличиваем лимит, так как нет отдельной страницы списка)
    all_tours = Tour.objects.filter(is_active=True).order_by('-created_at')
    tours = []
    
    # Фильтруем туры, оставляя только те, у которых есть хотя бы одно непрошедшее мероприятие
    for tour in all_tours:
        # Получаем связанные мероприятия
        tour_events = tour.events.filter(status=EventStatus.ACTIVE)
        has_upcoming_events = False
        
        # Проверяем каждое мероприятие
        for event in tour_events:
            if not event.is_past():
                has_upcoming_events = True
                break
        
        # Если у тура есть непрошедшие мероприятия, добавляем его в список
        if has_upcoming_events:
            tours.append(tour)
            if len(tours) >= 6:  # Ограничиваем количество туров до 6
                break
    
    # Получаем часто задаваемые вопросы (все, так как нет отдельной страницы)
    questions = Question.objects.all().order_by('position')
    
    context = {
        'banners': banners,
        'upcoming_events': upcoming_events,
        'tours': tours,
        'questions': questions,
    }
    return render(request, 'core/index.html', context)

def archive(request):
    """Страница архива мероприятий"""
    # Получаем все прошедшие мероприятия
    past_events = []
    all_events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('-date', '-time')
    
    # Получаем ближайшие мероприятия для отображения ссылки в меню
    upcoming_events = []
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    
    # Заполняем список прошедших мероприятий
    for event in all_events:
        if event.is_past():
            past_events.append(event)
    
    # Заполняем список предстоящих мероприятий
    for event in events:
        if not event.is_past():
            upcoming_events.append(event)
            if len(upcoming_events) >= 12:
                break
    
    # Получаем активные туры для отображения ссылки в меню
    all_tours = Tour.objects.filter(is_active=True).order_by('-created_at')
    tours = []
    
    # Фильтруем туры, оставляя только те, у которых есть хотя бы одно непрошедшее мероприятие
    for tour in all_tours:
        # Получаем связанные мероприятия
        tour_events = tour.events.filter(status=EventStatus.ACTIVE)
        has_upcoming_events = False
        
        # Проверяем каждое мероприятие
        for event in tour_events:
            if not event.is_past():
                has_upcoming_events = True
                break
        
        # Если у тура есть непрошедшие мероприятия, добавляем его в список
        if has_upcoming_events:
            tours.append(tour)
            if len(tours) >= 6:  # Ограничиваем количество туров до 6
                break
    
    # Получаем часто задаваемые вопросы для отображения ссылки в меню
    questions = Question.objects.all().order_by('position')
    
    # Города для фильтрации
    cities = City.objects.all().order_by('name')
    
    # Типы мероприятий для фильтрации
    event_types = EventType.objects.all().order_by('name')
    
    context = {
        'past_events': past_events,
        'title': 'Архив мероприятий',
        'upcoming_events': upcoming_events,
        'tours': tours,
        'questions': questions,
        'cities': cities,
        'event_types': event_types,
    }
    return render(request, 'core/archive.html', context)

def privacy_policy(request):
    """Страница политики конфиденциальности"""
    # Получаем данные для отображения ссылок в меню
    upcoming_events = []
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    
    for event in events:
        if not event.is_past():
            upcoming_events.append(event)
            if len(upcoming_events) >= 12:
                break
    
    all_tours = Tour.objects.filter(is_active=True).order_by('-created_at')
    tours = []
    
    # Фильтруем туры, оставляя только те, у которых есть хотя бы одно непрошедшее мероприятие
    for tour in all_tours:
        # Получаем связанные мероприятия
        tour_events = tour.events.filter(status=EventStatus.ACTIVE)
        has_upcoming_events = False
        
        # Проверяем каждое мероприятие
        for event in tour_events:
            if not event.is_past():
                has_upcoming_events = True
                break
        
        # Если у тура есть непрошедшие мероприятия, добавляем его в список
        if has_upcoming_events:
            tours.append(tour)
            if len(tours) >= 6:  # Ограничиваем количество туров до 6
                break
    
    questions = Question.objects.all().order_by('position')
    
    context = {
        'title': 'Политика конфиденциальности',
        'upcoming_events': upcoming_events,
        'tours': tours,
        'questions': questions,
    }
    return render(request, 'core/privacy_policy.html', context)

def terms_of_service(request):
    """Страница пользовательского соглашения"""
    # Получаем данные для отображения ссылок в меню
    upcoming_events = []
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    
    for event in events:
        if not event.is_past():
            upcoming_events.append(event)
            if len(upcoming_events) >= 12:
                break
    
    all_tours = Tour.objects.filter(is_active=True).order_by('-created_at')
    tours = []
    
    # Фильтруем туры, оставляя только те, у которых есть хотя бы одно непрошедшее мероприятие
    for tour in all_tours:
        # Получаем связанные мероприятия
        tour_events = tour.events.filter(status=EventStatus.ACTIVE)
        has_upcoming_events = False
        
        # Проверяем каждое мероприятие
        for event in tour_events:
            if not event.is_past():
                has_upcoming_events = True
                break
        
        # Если у тура есть непрошедшие мероприятия, добавляем его в список
        if has_upcoming_events:
            tours.append(tour)
            if len(tours) >= 6:  # Ограничиваем количество туров до 6
                break
    
    questions = Question.objects.all().order_by('position')
    
    context = {
        'title': 'Пользовательское соглашение',
        'upcoming_events': upcoming_events,
        'tours': tours,
        'questions': questions,
    }
    return render(request, 'core/terms_of_service.html', context)

def custom_404(request, exception):
    """Страница 404 ошибки"""
    # Получаем данные для отображения ссылок в меню
    upcoming_events = []
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    
    for event in events:
        if not event.is_past():
            upcoming_events.append(event)
            if len(upcoming_events) >= 12:
                break
    
    all_tours = Tour.objects.filter(is_active=True).order_by('-created_at')
    tours = []
    
    # Фильтруем туры, оставляя только те, у которых есть хотя бы одно непрошедшее мероприятие
    for tour in all_tours:
        # Получаем связанные мероприятия
        tour_events = tour.events.filter(status=EventStatus.ACTIVE)
        has_upcoming_events = False
        
        # Проверяем каждое мероприятие
        for event in tour_events:
            if not event.is_past():
                has_upcoming_events = True
                break
        
        # Если у тура есть непрошедшие мероприятия, добавляем его в список
        if has_upcoming_events:
            tours.append(tour)
            if len(tours) >= 6:  # Ограничиваем количество туров до 6
                break
    
    questions = Question.objects.all().order_by('position')
    
    context = {
        'title': 'Страница не найдена',
        'upcoming_events': upcoming_events,
        'tours': tours,
        'questions': questions,
    }
    return render(request, 'core/404.html', context, status=404)
