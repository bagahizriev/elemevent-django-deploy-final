function showSlide(index, items, indicators, currentIndex) {
	// Скрываем все слайды
	items.forEach(item => {
		item.classList.add('hidden')
		item.classList.remove('block')
	})

	// Отображаем нужный слайд
	items[index].classList.remove('hidden')
	items[index].classList.add('block')

	// Обновляем индикаторы
	indicators.forEach((indicator, i) => {
		if (i === index) {
			indicator.classList.add('bg-primary')
			indicator.classList.remove('bg-muted')
		} else {
			indicator.classList.remove('bg-primary')
			indicator.classList.add('bg-muted')
		}
	})

	return index
}

export function initCarousel() {
	const mainCarousel = document.getElementById('mainCarousel')
	if (mainCarousel) {
		const items = mainCarousel.querySelectorAll('.carousel-item')
		const indicators = document.querySelectorAll('.carousel-indicator')
		const prevButton = mainCarousel.querySelector('.carousel-control-prev')
		const nextButton = mainCarousel.querySelector('.carousel-control-next')
		let currentIndex = 0
		let interval

		// Переключение на следующий слайд
		function nextSlide() {
			let newIndex = currentIndex + 1
			if (newIndex >= items.length) {
				newIndex = 0
			}
			currentIndex = showSlide(newIndex, items, indicators, currentIndex)
		}

		// Переключение на предыдущий слайд
		function prevSlide() {
			let newIndex = currentIndex - 1
			if (newIndex < 0) {
				newIndex = items.length - 1
			}
			currentIndex = showSlide(newIndex, items, indicators, currentIndex)
		}

		// Настраиваем автоматическое переключение
		function startAutoSlide() {
			interval = setInterval(nextSlide, 5000) // Каждые 5 секунд
		}

		// Обработчики событий для кнопок и индикаторов
		if (nextButton) {
			nextButton.addEventListener('click', function () {
				nextSlide()
				clearInterval(interval)
				startAutoSlide()
			})
		}

		if (prevButton) {
			prevButton.addEventListener('click', function () {
				prevSlide()
				clearInterval(interval)
				startAutoSlide()
			})
		}

		// Обработчики для индикаторов
		indicators.forEach((indicator, index) => {
			indicator.addEventListener('click', function () {
				currentIndex = showSlide(index, items, indicators, currentIndex)
				clearInterval(interval)
				startAutoSlide()
			})
		})

		// Запускаем автоматическое переключение
		if (items.length > 1) {
			startAutoSlide()
		}
	}
}
