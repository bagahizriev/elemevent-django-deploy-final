#!/bin/bash

# Скрипт для развертывания Django приложения с Docker

set -e

echo "🚀 Начинаем развертывание elemevent..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker установлен. Перелогиньтесь для применения изменений."
    exit 1
fi

# Проверяем наличие Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не найден. Устанавливаем..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose установлен."
fi

# Создаем необходимые директории
echo "📁 Создаем необходимые директории..."
mkdir -p certbot/conf certbot/www backups logs media

# Проверяем .env файл
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "📋 Скопируйте .env.production в .env и заполните все переменные:"
    echo "   cp .env.production .env"
    echo "   nano .env"
    exit 1
fi

# Загружаем переменные окружения
source .env

# Проверяем обязательные переменные
if [ -z "$SECRET_KEY" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DOMAIN" ]; then
    echo "❌ Не все обязательные переменные окружения установлены!"
    echo "Проверьте: SECRET_KEY, DB_PASSWORD, DOMAIN"
    exit 1
fi

echo "🔧 Настраиваем файрволл..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "🔨 Собираем Docker образы..."
docker-compose build --no-cache

echo "🗄️ Запускаем базу данных..."
docker-compose up -d db redis

echo "⏳ Ждем готовности базы данных..."
sleep 30

echo "🔄 Выполняем миграции..."
docker-compose run --rm web python manage.py migrate

echo "👤 Создаем суперпользователя (если нужно)..."
echo "Хотите создать суперпользователя? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    docker-compose run --rm web python manage.py createsuperuser
fi

echo "📦 Собираем статические файлы..."
docker-compose run --rm web python manage.py collectstatic --noinput

echo "🌐 Получаем SSL сертификат..."
# Сначала запускаем nginx без SSL
docker-compose run --rm certbot certbot certonly --webroot --webroot-path /var/www/certbot --email admin@${DOMAIN} --agree-tos --no-eff-email -d ${DOMAIN} -d www.${DOMAIN}

echo "🚀 Запускаем все сервисы..."
docker-compose up -d

echo "🎯 Настраиваем автообновление SSL сертификата..."
(crontab -l 2>/dev/null; echo "0 12 * * * cd $(pwd) && docker-compose exec certbot certbot renew --quiet && docker-compose exec nginx nginx -s reload") | crontab -

echo "📊 Настраиваем автоматический бэкап базы данных..."
(crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && docker-compose exec db pg_dump -U ${DB_USER} ${DB_NAME} > backups/backup_\$(date +\%Y\%m\%d_\%H\%M\%S).sql") | crontab -

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "🌟 Ваше приложение доступно по адресам:"
echo "   https://${DOMAIN}"
echo "   https://www.${DOMAIN}"
echo ""
echo "🔧 Полезные команды:"
echo "   Логи приложения:    docker-compose logs -f web"
echo "   Логи Nginx:         docker-compose logs -f nginx"
echo "   Логи базы данных:   docker-compose logs -f db"
echo "   Статус сервисов:    docker-compose ps"
echo "   Остановить все:     docker-compose down"
echo "   Рестарт:           docker-compose restart"
echo ""
echo "📁 Файлы:"
echo "   Логи приложения:   ./logs/"
echo "   Медиа файлы:       ./media/"
echo "   Бэкапы БД:         ./backups/"
echo ""

# Показываем статус сервисов
echo "📊 Статус сервисов:"
docker-compose ps