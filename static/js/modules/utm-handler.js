const UTM_PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
const LOCAL_STORAGE_KEY = 'utm_params_storage'

export function initUtmHandler() {
	// Сохраняем UTM метки при загрузке страницы
	saveUtmParams()

	// Добавляем UTM метки к кнопкам покупки билетов
	addUtmToTicketButtons()
}

function getCurrentPagePath() {
	// Получаем путь текущей страницы без параметров
	return window.location.pathname
}

function getCurrentEventSlug() {
	// Получаем slug мероприятия из URL, если мы на странице мероприятия
	const path = getCurrentPagePath()
	const eventPathRegex = /^\/events\/([^\/]+)\/?$/
	const match = path.match(eventPathRegex)
	return match ? match[1] : null
}

function isEventPage() {
	return getCurrentEventSlug() !== null
}

function isEventPath(path) {
	// Проверяем, является ли путь страницей мероприятия
	return /^\/events\/[^\/]+\/?$/.test(path)
}

function saveUtmParams() {
	const urlParams = new URLSearchParams(window.location.search)
	const currentUtmParams = {}
	let hasUtmParams = false

	// Собираем все UTM метки из URL
	UTM_PARAMS.forEach(param => {
		const value = urlParams.get(param)
		if (value) {
			currentUtmParams[param] = value
			hasUtmParams = true
		}
	})

	if (!hasUtmParams) return

	// Получаем текущее хранилище UTM меток
	let storage = getUtmStorage()
	const currentPath = getCurrentPagePath()
	const currentEventSlug = getCurrentEventSlug()

	if (currentEventSlug) {
		// Если мы на странице мероприятия, сохраняем метки только для этого мероприятия
		storage.events[currentEventSlug] = {
			params: currentUtmParams,
			timestamp: Date.now(),
		}
	}

	// Сохраняем последние полученные метки только если мы не на странице мероприятия
	if (!isEventPage()) {
		storage.latest = {
			params: currentUtmParams,
			path: currentPath,
			timestamp: Date.now(),
		}
	}

	// Сохраняем обновленное хранилище
	localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(storage))
}

function getUtmStorage() {
	const storage = localStorage.getItem(LOCAL_STORAGE_KEY)
	if (!storage) {
		return {
			events: {}, // Метки для конкретных мероприятий
			latest: null, // Последние полученные метки (для не-event страниц)
		}
	}
	return JSON.parse(storage)
}

function getRelevantUtmParams() {
	const storage = getUtmStorage()
	const currentEventSlug = getCurrentEventSlug()

	if (isEventPage()) {
		// Если мы на странице мероприятия
		if (currentEventSlug && storage.events[currentEventSlug]) {
			// Сначала пробуем использовать метки этого мероприятия
			return storage.events[currentEventSlug].params
		} else if (storage.latest && !isEventPath(storage.latest.path)) {
			// Если нет меток мероприятия, используем последние метки,
			// но только если они не были получены на странице другого мероприятия
			return storage.latest.params
		}
		return null
	}

	// Если мы не на странице мероприятия, используем последние сохранённые метки
	return storage.latest ? storage.latest.params : null
}

function addUtmParamsToUrl(url) {
	const utmParams = getRelevantUtmParams()
	if (!utmParams) return url

	const urlObj = new URL(url)

	// Добавляем UTM метки к URL
	Object.entries(utmParams).forEach(([key, value]) => {
		urlObj.searchParams.set(key, value)
	})

	return urlObj.toString()
}

function getUtmParamsString() {
	const utmParams = getRelevantUtmParams()
	if (!utmParams) return ''

	const params = new URLSearchParams()
	Object.entries(utmParams).forEach(([key, value]) => {
		params.set(key, value)
	})

	return params.toString()
}

function addUtmToTicketButtons() {
	// Обрабатываем только прямые ссылки (DIRECT)
	const ticketButtons = document.querySelectorAll('.ticket-button')
	ticketButtons.forEach(button => {
		if (button.href) {
			const originalUrl = button.href
			button.href = addUtmParamsToUrl(originalUrl)
		}
	})
}
