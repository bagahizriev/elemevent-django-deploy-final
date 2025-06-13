document.addEventListener('DOMContentLoaded', function () {
	const slugField = document.getElementById('id_slug')
	// Проверяем, находимся ли мы на странице редактирования (а не создания)
	// URL страницы редактирования содержит "change", а создания - "add"
	const isEditPage = window.location.pathname.includes('/change/')

	if (slugField && isEditPage) {
		// Определяем тип объекта (тур или мероприятие) по URL
		const isTour = window.location.pathname.includes('/tours/tour/')
		const message = isTour ? 'Внимание! Изменение URL приведет к тому, что пользователи не смогут попасть на страницу тура по старой ссылке.' : 'Внимание! Изменение URL приведет к тому, что пользователи не смогут попасть на страницу мероприятия по старой ссылке.'

		let isConfirmed = false

		// Добавляем обработчик события focus
		slugField.addEventListener('focus', function () {
			if (!isConfirmed) {
				if (confirm(message + '\n\nВы уверены, что хотите изменить URL?')) {
					// Если пользователь подтвердил, разрешаем редактирование
					isConfirmed = true
					slugField.removeAttribute('readonly')
				} else {
					// Если пользователь отменил, запрещаем редактирование
					slugField.blur()
				}
			}
		})

		// Добавляем обработчик события blur
		slugField.addEventListener('blur', function () {
			if (!slugField.value.trim()) {
				// Если поле пустое после редактирования, сбрасываем флаг
				isConfirmed = false
			}
			if (!isConfirmed) {
				// Делаем поле readonly только если редактирование не подтверждено
				slugField.setAttribute('readonly', 'readonly')
			}
		})

		// Изначально делаем поле readonly
		if (!isConfirmed) {
			slugField.setAttribute('readonly', 'readonly')
		}
	}
})
