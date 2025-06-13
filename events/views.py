from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Event, City, EventType, AgeRestriction, EventStatus
from django.http import Http404
from tours.models import Tour
from faq.models import Question
from django.utils import timezone

def event_list(request):
    """Список всех мероприятий"""
    # Получаем все активные мероприятия, отсортированные по дате и времени
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    
    # Фильтрация по городу
    city_id = request.GET.get('city')
    if city_id:
        try:
            city = City.objects.get(id=city_id)
            events = events.filter(city=city)
        except City.DoesNotExist:
            pass
    
    # Фильтрация по типу мероприятия
    event_type_id = request.GET.get('type')
    if event_type_id:
        try:
            event_type = EventType.objects.get(id=event_type_id)
            events = events.filter(event_type=event_type)
        except EventType.DoesNotExist:
            pass
    
    # Пагинация (12 мероприятий на страницу)
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем данные для отображения ссылок в меню
    upcoming_events = []
    for event in events:
        if not event.is_past():
            upcoming_events.append(event)
            if len(upcoming_events) >= 12:
                break
    
    tours = Tour.objects.filter(is_active=True).order_by('-created_at')[:6]
    questions = Question.objects.all().order_by('position')
    
    # Города для фильтрации
    cities = City.objects.all().order_by('name')
    
    # Типы мероприятий для фильтрации
    event_types = EventType.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'title': 'Мероприятия',
        'upcoming_events': upcoming_events,
        'tours': tours,
        'questions': questions,
        'cities': cities,
        'event_types': event_types,
        'selected_city': city_id,
        'selected_type': event_type_id,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, slug):
    """Детальная страница мероприятия"""
    # Получаем мероприятие по slug
    event = get_object_or_404(Event, slug=slug)
    
    # Если мероприятие в статусе черновика, возвращаем 404
    if event.status == EventStatus.DRAFT:
        raise Http404("Мероприятие не найдено")
    
    # Проверяем, прошло ли мероприятие
    is_past = event.is_past()
    
    # Получаем другие мероприятия из того же города, сортируем по дате (ближайшие)
    all_related_events = Event.objects.filter(
        city=event.city, 
        status=EventStatus.ACTIVE
    ).exclude(id=event.id).order_by('date', 'time')
    
    # Фильтруем прошедшие мероприятия
    related_events = []
    for related_event in all_related_events:
        if not related_event.is_past():
            related_events.append(related_event)
            if len(related_events) >= 3:  # Ограничиваем количество до 3
                break
    
    # Получаем данные для отображения ссылок в меню
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    upcoming_events = []
    for e in events:
        if not e.is_past():
            upcoming_events.append(e)
            if len(upcoming_events) >= 12:
                break
    
    tours = Tour.objects.filter(is_active=True).order_by('-created_at')[:6]
    questions = Question.objects.all().order_by('position')
    
    context = {
        'event': event,
        'related_events': related_events,
        'upcoming_events': upcoming_events,
        'tours': tours,
        'questions': questions,
        'is_archive': is_past and event.status == EventStatus.ACTIVE,  # Архив только для активных мероприятий
        'is_stopped': event.is_stopped(),  # Флаг для приостановленных мероприятий
        'is_cancelled': event.is_cancelled(),  # Флаг для отмененных мероприятий
    }
    return render(request, 'events/event_detail.html', context)
