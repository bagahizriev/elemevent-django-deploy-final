Давайте разберем всё по порядку:

1. **Добавленные зависимости и их назначение:**

- `django-cors-headers>=4.3.1`

  - Управляет CORS (Cross-Origin Resource Sharing) заголовками
  - Позволяет безопасно делать запросы к вашему API с других доменов
  - Использование:
    ```python
    # Уже добавлено в settings.py
    CORS_ALLOWED_ORIGINS = ['https://ваш-домен.ru']
    CORS_ALLOW_CREDENTIALS = True
    ```

- `sentry-sdk>=1.40.0`

  - Система мониторинга ошибок
  - Отслеживает ошибки в продакшене в реальном времени
  - Использование:
    1. Зарегистрируйтесь на sentry.io
    2. Создайте проект
    3. Получите DSN
    4. Добавьте в `.env` на сервере:
    ```
    SENTRY_DSN=ваш-dsn-ключ
    ```

- `django-cleanup>=8.1.0`
  - Автоматически удаляет старые файлы при их замене или удалении объекта
  - Особенно полезно для медиафайлов
  - Использование:
    ```python
    INSTALLED_APPS = [
        ...
        'django_cleanup.apps.CleanupConfig',  # всегда последним
    ]
    ```

2. **Что делать при реальном деплое:**

1) **Подготовка сервера:**

```bash
# Установка необходимых пакетов
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib supervisor

# Создание пользователя
sudo useradd -m -s /bin/bash elemevent
sudo usermod -aG www-data elemevent

# Создание директорий
sudo mkdir -p /var/www/elemevent/{static,media}
sudo chown -R elemevent:www-data /var/www/elemevent
```

2. **Настройка PostgreSQL:**

```bash
sudo -u postgres psql
CREATE DATABASE elemevent;
CREATE USER elemevent_user WITH PASSWORD 'ваш-сложный-пароль';
ALTER ROLE elemevent_user SET client_encoding TO 'utf8';
ALTER ROLE elemevent_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE elemevent_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE elemevent TO elemevent_user;
\q
```

3. **Настройка проекта:**

```bash
# Клонирование проекта
git clone ваш-репозиторий /var/www/elemevent/app

# Создание виртуального окружения
python3 -m venv /var/www/elemevent/venv
source /var/www/elemevent/venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
nano /var/www/elemevent/.env
```

4. **Содержимое `.env` на сервере:**

```bash
# Основные настройки Django
DEBUG=0
SECRET_KEY=новый-сложный-ключ
ALLOWED_HOSTS=ваш-домен.ru,www.ваш-домен.ru

# Настройки базы данных
DATABASE_URL=postgres://elemevent_user:ваш-пароль@localhost:5432/elemevent

# Пути к статическим и медиа файлам
STATIC_ROOT=/var/www/elemevent/static
MEDIA_ROOT=/var/www/elemevent/media

# Настройки безопасности
CSRF_TRUSTED_ORIGINS=https://ваш-домен.ru
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1

# Дополнительные настройки
SERVE_MEDIA_IN_PRODUCTION=1
```

5. **Настройка Supervisor** (создайте файл `/etc/supervisor/conf.d/elemevent.conf`):

```ini
[program:elemevent]
directory=/var/www/elemevent/app
command=/var/www/elemevent/venv/bin/gunicorn elemevent.wsgi:application --workers 3 --bind unix:/var/www/elemevent/elemevent.sock
user=elemevent
autostart=true
autorestart=true
stderr_logfile=/var/log/elemevent/err.log
stdout_logfile=/var/log/elemevent/out.log

[supervisord]
logfile=/var/log/supervisor/supervisord.log
```

6. **Настройка Nginx** (создайте файл `/etc/nginx/sites-available/elemevent`):

```nginx
server {
    listen 80;
    server_name ваш-домен.ru www.ваш-домен.ru;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /var/www/elemevent;
    }

    location /media/ {
        root /var/www/elemevent;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/elemevent/elemevent.sock;
    }
}
```

7. **Настройка SSL** с Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен.ru -d www.ваш-домен.ru
```

8. **Финальные команды:**

```bash
# Сбор статических файлов
python manage.py collectstatic

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Перезапуск служб
sudo supervisorctl restart elemevent
sudo service nginx restart
```

3. **Разница между локальной разработкой и сервером:**

Локально:

- DEBUG=1
- Используются локальные пути для static/media
- Разработка через `python manage.py runserver`
- Возможность использовать Django Debug Toolbar

На сервере:

- DEBUG=0
- Абсолютные пути для static/media
- Gunicorn + Nginx для раздачи
- Включены все настройки безопасности
- Настроен SSL
- Включен мониторинг ошибок через Sentry

Если хотите тестировать продакшен-подобное окружение локально:

1. Установите и настройте PostgreSQL
2. Используйте те же настройки в `.env`, но с локальными путями
3. Запускайте через gunicorn вместо `runserver`

Это даст вам среду, максимально приближенную к продакшену, но на локальной машине.

```
python manage.py collectstatic
```

```
gunicorn elemevent.wsgi:application --bind 127.0.0.1:8000 --workers 3 --reload
```

```
gunicorn elemevent.wsgi:application --bind 0.0.0.0:8000 --workers 3 --reload
```
