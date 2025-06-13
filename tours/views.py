from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Tour
from events.models import Event, EventStatus
from faq.models import Question
from django.utils import timezone

def tour_list(request):
    """Список всех туров"""
    # Получаем все активные туры
    all_tours = Tour.objects.filter(is_active=True).order_by('-created_at')
    filtered_tours = []
    
    # Фильтруем туры, оставляя только те, у которых есть хотя бы одно непрошедшее мероприятие
    for tour in all_tours:
        tour_events = tour.events.filter(status=EventStatus.ACTIVE)
        has_upcoming_events = False
        
        for event in tour_events:
            if not event.is_past():
                has_upcoming_events = True
                break
        
        if has_upcoming_events:
            filtered_tours.append(tour)
    
    # Пагинация (9 туров на страницу)
    paginator = Paginator(filtered_tours, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем данные для отображения ссылок в меню
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    upcoming_events = []
    for event in events:
        if not event.is_past():
            upcoming_events.append(event)
            if len(upcoming_events) >= 12:
                break
    
    questions = Question.objects.all().order_by('position')
    
    context = {
        'page_obj': page_obj,
        'title': 'Туры',
        'upcoming_events': upcoming_events,
        'tours': filtered_tours,
        'questions': questions,
    }
    return render(request, 'tours/tour_list.html', context)

def tour_detail(request, slug):
    """Детальная страница тура"""
    # Получаем тур по slug
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    
    # Получаем мероприятия тура, отсортированные по дате
    all_tour_events = tour.events.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    
    # Разделяем мероприятия на предстоящие и прошедшие
    tour_events = []  # Предстоящие мероприятия
    past_tour_events = []  # Прошедшие мероприятия
    
    # Флаги для проверки наличия виджетов
    has_ticketscloud = False
    has_radario = False
    
    for event in all_tour_events:
        if not event.is_past():
            tour_events.append(event)
            # Проверяем наличие виджетов
            if event.ticket_system == 'TICKETSCLOUD' and event.ticketscloud_event_id and event.ticketscloud_token:
                has_ticketscloud = True
            elif event.ticket_system == 'RADARIO' and event.radario_key:
                has_radario = True
        else:
            past_tour_events.append(event)
    
    # Определяем статус тура
    tour_status = "upcoming"  # upcoming, past, empty
    if not all_tour_events:
        tour_status = "empty"  # Нет мероприятий вообще
    elif not tour_events:
        tour_status = "past"  # Все мероприятия прошли
    
    # Получаем данные для отображения ссылок в меню
    events = Event.objects.filter(status=EventStatus.ACTIVE).order_by('date', 'time')
    upcoming_events = []
    for event in events:
        if not event.is_past():
            upcoming_events.append(event)
            if len(upcoming_events) >= 12:
                break
    
    # Получаем другие туры для отображения ссылок
    all_tours = Tour.objects.filter(is_active=True).exclude(pk=tour.pk).order_by('-created_at')
    tours = []
    
    # Фильтруем туры, оставляя только те, у которых есть хотя бы одно непрошедшее мероприятие
    for other_tour in all_tours:
        tour_events_check = other_tour.events.filter(status=EventStatus.ACTIVE)
        has_upcoming_events = False
        
        for event in tour_events_check:
            if not event.is_past():
                has_upcoming_events = True
                break
        
        if has_upcoming_events:
            tours.append(other_tour)
            if len(tours) >= 6:
                break
    
    questions = Question.objects.all().order_by('position')
    
    context = {
        'tour': tour,
        'tour_events': tour_events,
        'past_tour_events': past_tour_events,
        'tour_status': tour_status,
        'upcoming_events': upcoming_events,
        'tours': tours,
        'questions': questions,
        'has_ticketscloud': has_ticketscloud,
        'has_radario': has_radario,
    }
    return render(request, 'tours/tour_detail.html', context)
