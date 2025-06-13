export function initFaq() {
	const faqButtons = document.querySelectorAll('[id^="faq-button-"]')

	faqButtons.forEach(button => {
		button.addEventListener('click', function () {
			const contentId = this.getAttribute('aria-controls')
			const content = document.getElementById(contentId)
			const isExpanded = this.getAttribute('aria-expanded') === 'true'

			// Закрываем все остальные открытые вопросы
			faqButtons.forEach(otherButton => {
				if (otherButton !== this && otherButton.getAttribute('aria-expanded') === 'true') {
					const otherId = otherButton.getAttribute('aria-controls')
					const otherContent = document.getElementById(otherId)
					otherButton.setAttribute('aria-expanded', 'false')
					otherContent.classList.add('hidden')
					otherButton.querySelector('.faq-arrow').classList.remove('expanded')
				}
			})

			// Переключаем текущий вопрос
			this.setAttribute('aria-expanded', !isExpanded)
			content.classList.toggle('hidden')

			// Анимируем иконку
			const arrow = this.querySelector('.faq-arrow')
			arrow.classList.toggle('expanded')
		})
	})

	// Добавляем поддержку клавиатуры
	faqButtons.forEach((button, index) => {
		button.addEventListener('keydown', function (e) {
			const buttons = Array.from(faqButtons)

			switch (e.key) {
				case 'ArrowUp':
					e.preventDefault()
					const prevButton = buttons[index - 1] || buttons[buttons.length - 1]
					prevButton.focus()
					break
				case 'ArrowDown':
					e.preventDefault()
					const nextButton = buttons[index + 1] || buttons[0]
					nextButton.focus()
					break
				case 'Home':
					e.preventDefault()
					buttons[0].focus()
					break
				case 'End':
					e.preventDefault()
					buttons[buttons.length - 1].focus()
					break
			}
		})
	})
}
