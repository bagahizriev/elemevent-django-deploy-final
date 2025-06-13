class EventPush {
	constructor(eventId, content) {
		this.eventId = eventId
		this.content = content
		this.pushElement = document.getElementById('eventPush')
	}

	adjustPushAlignment() {
		if (!this.pushElement) return

		const contentElement = this.pushElement.querySelector('.push-content')

		// Временно делаем элемент видимым для измерения высоты
		const wasHidden = this.pushElement.style.display === 'none'
		if (wasHidden) {
			this.pushElement.style.visibility = 'hidden'
			this.pushElement.style.display = 'flex'
		}

		if (contentElement.clientHeight <= 24) {
			this.pushElement.classList.add('items-center')
			this.pushElement.classList.remove('items-start')
		} else {
			this.pushElement.classList.add('items-start')
			this.pushElement.classList.remove('items-center')
		}

		// Возвращаем исходное состояние
		if (wasHidden) {
			this.pushElement.style.display = 'none'
			this.pushElement.style.visibility = 'visible'
		}
	}

	show() {
		if (!this.pushElement) return
		this.adjustPushAlignment()
		this.pushElement.style.display = 'flex'
	}

	close() {
		if (!this.pushElement) return
		this.pushElement.style.display = 'none'
		const pushInfo = {
			hidden: true,
			contentHash: this.getContentHash(),
		}
		localStorage.setItem(`eventPush_${this.eventId}`, JSON.stringify(pushInfo))
	}

	getContentHash() {
		return btoa(encodeURIComponent(this.content)).replace(/=/g, '')
	}

	init() {
		if (!this.pushElement) return

		const storedPushInfo = localStorage.getItem(`eventPush_${this.eventId}`)

		if (storedPushInfo) {
			try {
				const pushInfo = JSON.parse(storedPushInfo)
				const currentContentHash = this.getContentHash()

				if (!pushInfo.hidden || pushInfo.contentHash !== currentContentHash) {
					this.show()
					if (pushInfo.contentHash !== currentContentHash) {
						localStorage.removeItem(`eventPush_${this.eventId}`)
					}
				}
			} catch (e) {
				this.show()
				localStorage.removeItem(`eventPush_${this.eventId}`)
			}
		} else {
			this.show()
		}

		// Добавляем обработчик для кнопки закрытия
		const closeButton = this.pushElement.querySelector('button')
		if (closeButton) {
			closeButton.onclick = () => this.close()
		}

		// Проверяем выравнивание после полной загрузки страницы
		window.addEventListener('load', () => this.adjustPushAlignment())
	}
}
