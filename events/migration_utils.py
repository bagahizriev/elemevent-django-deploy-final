"""
Утилиты для миграции данных из старых моделей в новые.
Используется в data migrations.
"""

def migrate_cities_from_events(apps, schema_editor):
    """
    Создает записи в модели City на основе существующих данных в модели Event.
    Используется в data migration.
    """
    Event = apps.get_model('events', 'Event')
    City = apps.get_model('events', 'City')
    
    # Получаем уникальные пары city/timezone из существующих событий
    city_timezone_pairs = Event.objects.values_list('city', 'timezone').distinct()
    
    # Создаем записи City для каждой уникальной пары
    for city_name, timezone in city_timezone_pairs:
        City.objects.get_or_create(name=city_name, timezone=timezone)
    
    # Обновляем ссылки в событиях
    for event in Event.objects.all():
        city_obj, _ = City.objects.get_or_create(name=event.city, timezone=event.timezone)
        event.city_new = city_obj
        event.save(update_fields=['city_new'])

def migrate_event_types_from_events(apps, schema_editor):
    """
    Создает записи в модели EventType на основе существующих данных в модели Event.
    Используется в data migration.
    """
    Event = apps.get_model('events', 'Event')
    EventType = apps.get_model('events', 'EventType')
    
    # Получаем уникальные event_type из существующих событий
    event_types = Event.objects.exclude(event_type__isnull=True).values_list('event_type', flat=True).distinct()
    
    # Создаем записи EventType для каждого уникального типа
    for event_type_name in event_types:
        if event_type_name:
            EventType.objects.get_or_create(name=event_type_name)
    
    # Обновляем ссылки в событиях
    for event in Event.objects.exclude(event_type__isnull=True):
        if event.event_type:
            event_type_obj, _ = EventType.objects.get_or_create(name=event.event_type)
            event.event_type_new = event_type_obj
            event.save(update_fields=['event_type_new'])

def migrate_age_restrictions_from_events(apps, schema_editor):
    """
    Создает записи в модели AgeRestriction на основе существующих данных в модели Event.
    Используется в data migration.
    """
    Event = apps.get_model('events', 'Event')
    AgeRestriction = apps.get_model('events', 'AgeRestriction')
    
    # Получаем уникальные age_restriction из существующих событий
    age_restrictions = Event.objects.exclude(age_restriction__isnull=True).values_list('age_restriction', flat=True).distinct()
    
    # Создаем записи AgeRestriction для каждого уникального ограничения
    for age_restriction_name in age_restrictions:
        if age_restriction_name:
            AgeRestriction.objects.get_or_create(name=age_restriction_name)
    
    # Обновляем ссылки в событиях
    for event in Event.objects.exclude(age_restriction__isnull=True):
        if event.age_restriction:
            age_restriction_obj, _ = AgeRestriction.objects.get_or_create(name=event.age_restriction)
            event.age_restriction_new = age_restriction_obj
            event.save(update_fields=['age_restriction_new']) 