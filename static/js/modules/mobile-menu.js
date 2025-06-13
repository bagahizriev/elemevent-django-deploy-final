export function initMobileMenu() {
	const burgerBtn = document.getElementById('burger-menu-btn')
	const closeBtn = document.getElementById('close-menu-btn')
	const mobileMenu = document.getElementById('mobile-menu')
	const overlay = document.getElementById('mobile-menu-overlay')
	const mobileMenuLinks = mobileMenu.querySelectorAll('a')

	function openMenu() {
		mobileMenu.classList.remove('translate-x-full')
		overlay.classList.remove('hidden')
		document.body.style.overflow = 'hidden'
	}

	function closeMenu() {
		mobileMenu.classList.add('translate-x-full')
		overlay.classList.add('hidden')
		document.body.style.overflow = ''
	}

	burgerBtn.addEventListener('click', openMenu)
	closeBtn.addEventListener('click', closeMenu)
	overlay.addEventListener('click', closeMenu)

	// Закрываем меню при клике на ссылку
	mobileMenuLinks.forEach(link => {
		link.addEventListener('click', closeMenu)
	})
}
