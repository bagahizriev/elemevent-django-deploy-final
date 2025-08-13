#!/usr/bin/env python3
"""
Скрипт для проверки здоровья Django приложения
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elemevent.settings')
django.setup()

from django.db import connections
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_GET
def health_check(request):
    """
    Endpoint для проверки здоровья приложения
    """
    status = {
        'status': 'ok',
        'database': 'unknown',
        'cache': 'unknown',
        'details': {}
    }
    
    # Проверяем соединение с базой данных
    try:
        db_conn = connections['default']
        db_conn.cursor()
        status['database'] = 'ok'
    except Exception as e:
        status['database'] = 'error'
        status['details']['database_error'] = str(e)
        status['status'] = 'error'
    
    # Проверяем кэш (Redis)
    try:
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            status['cache'] = 'ok'
        else:
            status['cache'] = 'error'
            status['status'] = 'error'
    except Exception as e:
        status['cache'] = 'error'
        status['details']['cache_error'] = str(e)
        status['status'] = 'error'
    
    # Возвращаем результат
    return JsonResponse(status, status=200 if status['status'] == 'ok' else 503)

def run_health_check():
    """
    Запуск проверки здоровья из командной строки
    """
    try:
        # Проверяем базу данных
        db_conn = connections['default']
        db_conn.cursor()
        print("✅ База данных: OK")
        
        # Проверяем кэш
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            print("✅ Redis кэш: OK")
        else:
            print("❌ Redis кэш: ERROR")
            sys.exit(1)
            
        print("✅ Все системы работают нормально")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Ошибка при проверке здоровья: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_health_check()