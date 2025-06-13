import { initCarousel } from './modules/carousel.js'
import { initCitySelector } from './modules/city-selector.js'
import { initFaq } from './modules/faq.js'
import { initMobileMenu } from './modules/mobile-menu.js'
import { initUtmHandler } from './modules/utm-handler.js'

document.addEventListener('DOMContentLoaded', function () {
	initCitySelector()
	initCarousel()
	initFaq()
	initMobileMenu()
	initUtmHandler()
})
