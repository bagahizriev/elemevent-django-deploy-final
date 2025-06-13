django.jQuery(document).ready(function ($) {
	var ticketSystemSelect = $('#id_ticket_system')
	var ticketLinkField = $('.field-ticket_link')
	var ticketscloudFields = $('.field-ticketscloud_event_id, .field-ticketscloud_token')
	var radarioField = $('.field-radario_widget_code')

	function updateFieldVisibility() {
		var selectedSystem = ticketSystemSelect.val()

		// Скрываем все поля
		ticketLinkField.hide()
		ticketscloudFields.hide()
		radarioField.hide()

		// Показываем нужные поля в зависимости от выбранного типа
		switch (selectedSystem) {
			case 'DIRECT':
				ticketLinkField.show()
				break
			case 'TICKETSCLOUD':
				ticketscloudFields.show()
				break
			case 'RADARIO':
				radarioField.show()
				break
		}
	}

	// Обновляем видимость полей при загрузке страницы
	updateFieldVisibility()

	// Обновляем видимость полей при изменении типа билетной системы
	ticketSystemSelect.change(updateFieldVisibility)
})
