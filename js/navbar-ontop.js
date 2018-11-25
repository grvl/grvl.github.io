/**
 * navbar-ontop.js 1.0.0
 * Add .navbar-ontop class to navbar when the page is scrolled to top
 * Make sure to add this script to the <head> of page to avoid flickering on load
 */

(function() {

	var className = "navbar-ontop"

	function update() {
		// toggle className based on the scrollTop property of document
		var nav = document.querySelector(".navbar")

		if (window.scrollY > 15)
			nav.classList.remove(className)
		else
			nav.classList.add(className) 
	}

	window.addEventListener("scroll", function() {
		update()			
	})

})();