#!/bin/bash

# Скрипт мониторинга приложения

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📊 Мониторинг elemevent"
echo "========================"

# Проверяем статус контейнеров
echo -e "\n${YELLOW}🐳 Статус Docker контейнеров:${NC}"
docker-compose ps

# Проверяем использование ресурсов
echo -e "\n${YELLOW}💻 Использование ресурсов:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Проверяем место на диске
echo -e "\n${YELLOW}💾 Использование диска:${NC}"
df -h | grep -E '(Filesystem|/dev/)'

# Проверяем логи ошибок
echo -e "\n${YELLOW}📋 Последние ошибки в логах:${NC}"
if [ -f "logs/django.log" ]; then
    echo "Django ошибки (последние 5):"
    tail -5 logs/django.log | grep -i error || echo "Нет ошибок в логах Django"
fi

echo -e "\nNginx ошибки (последние 5):"
docker-compose logs --tail=50 nginx | grep -i error | tail -5 || echo "Нет ошибок в логах Nginx"

# Проверяем доступность сайта
echo -e "\n${YELLOW}🌐 Проверка доступности сайта:${NC}"
source .env
if curl -s -f "https://${DOMAIN}" > /dev/null; then
    echo -e "${GREEN}✅ Сайт доступен${NC}"
else
    echo -e "${RED}❌ Сайт недоступен${NC}"
fi

# Проверяем SSL сертификат
echo -e "\n${YELLOW}🔐 SSL сертификат:${NC}"
ssl_info=$(echo | openssl s_client -servername ${DOMAIN} -connect ${DOMAIN}:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL сертификат валиден${NC}"
    echo "$ssl_info"
else
    echo -e "${RED}❌ Проблема с SSL сертификатом${NC}"
fi

# Проверяем размер базы данных
echo -e "\n${YELLOW}🗄️ Размер базы данных:${NC}"
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME} -c "SELECT pg_size_pretty(pg_database_size('${DB_NAME}'));" 2>/dev/null || echo "Не удалось получить размер БД"

# Проверяем последний бэкап
echo -e "\n${YELLOW}💾 Последний бэкап:${NC}"
if [ -d "backups" ]; then
    latest_backup=$(ls -t backups/ | head -1 2>/dev/null)
    if [ -n "$latest_backup" ]; then
        echo "Последний бэкап: $latest_backup"
        echo "Размер: $(du -h "backups/$latest_backup" 2>/dev/null | cut -f1)"
    else
        echo "Бэкапы не найдены"
    fi
else
    echo "Директория backups не существует"
fi

# Проверяем обновления системы
echo -e "\n${YELLOW}🔄 Доступные обновления:${NC}"
if command -v apt &> /dev/null; then
    updates=$(apt list --upgradable 2>/dev/null | wc -l)
    echo "Доступно обновлений пакетов: $((updates-1))"
fi

echo -e "\n${GREEN}✅ Мониторинг завершен${NC}"