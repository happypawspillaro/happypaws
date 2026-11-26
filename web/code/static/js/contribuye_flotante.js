(() => {
	const boton = document.getElementById("contribuye-flotante");
	if (!boton) return;

	boton.addEventListener("click", (evento) => {
		if (!boton.classList.contains("is-minimizado")) return;

		evento.preventDefault();
		boton.classList.remove("is-minimizado");
	});

	const minimizar = () => {
		if (boton.matches(":hover, :focus-visible")) {
			window.setTimeout(minimizar, 1000);
			return;
		}
		boton.classList.add("is-minimizado");
	};

	window.setTimeout(minimizar, 5000);
})();
