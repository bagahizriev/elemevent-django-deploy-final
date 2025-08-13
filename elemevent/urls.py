"""
URL configuration for elemevent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from core.views import custom_404

# Маршруты приложений
urlpatterns = [
    path('z134sLtt652Ru/', admin.site.urls),
    path('', include('core.urls')),
    path('events/', include('events.urls')),
    path('tours/', include('tours.urls')),
]

# Добавляем маршруты для статических файлов
if settings.DEBUG:
    # В режиме отладки используем встроенный обработчик Django для статических и медиа-файлов
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Всегда добавляем маршрут для медиа-файлов, даже в продакшн-режиме
if settings.SERVE_MEDIA_IN_PRODUCTION:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Регистрируем обработчик 404 ошибки
handler404 = custom_404
