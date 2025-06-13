function removeDuplicateCities(cityOptions) {
	if (!cityOptions || cityOptions.length === 0) return

	const cities = new Set()
	cityOptions.forEach(option => {
		const cityName = option.getAttribute('data-city')
		if (cityName === 'all') {
			return // Skip the "All cities" option
		}

		if (cities.has(cityName)) {
			option.remove()
		} else {
			cities.add(cityName)
		}
	})
}

export function initCitySelector() {
	const citySelector = document.getElementById('citySelector')
	const cityDropdown = document.getElementById('cityDropdown')
	const citySearch = document.getElementById('citySearch')
	const cityOptions = document.querySelectorAll('.city-option')
	const selectedCityText = document.getElementById('selectedCity')
	const eventCards = document.querySelectorAll('.event-card')
	const noEventsMessage = document.getElementById('noEventsMessage')

	if (citySelector && cityDropdown) {
		removeDuplicateCities(cityOptions)

		// Обработчик кнопки выбора города
		const citySelectorButton = citySelector.querySelector('button')
		if (citySelectorButton) {
			citySelectorButton.addEventListener('click', function (e) {
				e.preventDefault()
				e.stopPropagation()
				cityDropdown.classList.toggle('hidden')
				this.classList.toggle('active')
			})
		}

		// Закрытие выпадающего списка при клике вне его
		document.addEventListener('click', function (e) {
			if (!citySelector.contains(e.target) && !cityDropdown.contains(e.target)) {
				cityDropdown.classList.add('hidden')
				citySelectorButton.classList.remove('active')
			}
		})

		// Предотвращаем закрытие при клике внутри выпадающего списка
		cityDropdown.addEventListener('click', function (e) {
			if (!e.target.classList.contains('city-option')) {
				e.stopPropagation()
			}
		})

		// Обработка поиска города
		if (citySearch) {
			citySearch.addEventListener('click', function (e) {
				e.stopPropagation()
			})

			citySearch.addEventListener('input', function () {
				const query = this.value.toLowerCase()
				cityOptions.forEach(option => {
					const cityName = option.textContent.toLowerCase()
					option.classList.toggle('hidden', cityName.indexOf(query) === -1)
				})
			})
		}

		// Выбор города
		cityOptions.forEach(option => {
			option.addEventListener('click', function () {
				const selectedCity = this.getAttribute('data-city')
				if (selectedCityText) {
					selectedCityText.textContent = selectedCity === 'all' ? 'Все города' : selectedCity
				}
				cityDropdown.classList.add('hidden')
				citySelectorButton.classList.remove('active')

				// Фильтрация событий
				let visibleEvents = 0
				if (eventCards && eventCards.length > 0) {
					eventCards.forEach(card => {
						const cityName = card.getAttribute('data-city')
						if (!cityName) return

						const shouldShow = selectedCity === 'all' || cityName.toLowerCase() === selectedCity.toLowerCase()
						card.classList.toggle('hidden', !shouldShow)
						if (shouldShow) visibleEvents++
					})
				}

				// Отображение сообщения, если нет событий
				if (noEventsMessage) {
					noEventsMessage.classList.toggle('hidden', visibleEvents > 0)
				}
			})
		})
	}
}
