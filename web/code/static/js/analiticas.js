// Google Analytics 4 (#58). base.html solo incluye este script si hay
// GA_MEASUREMENT_ID, y aquí gtag.js solo se descarga si la persona aceptó
// las cookies de analítica (static/js/consentimiento.js, #75).
(() => {
	const id = document.currentScript?.dataset.gaId;
	if (!id) return;
	let cargado = false;

	const cargar = () => {
		window[`ga-disable-${id}`] = false;
		if (cargado) return;
		cargado = true;
		window.dataLayer = window.dataLayer || [];
		window.gtag = function gtag() {
			// gtag.js espera el objeto arguments, no un arreglo.
			window.dataLayer.push(arguments);
		};
		window.gtag("js", new Date());
		window.gtag("config", id);
		const script = document.createElement("script");
		script.async = true;
		script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
		document.head.appendChild(script);
	};

	// Si cambia a "Solo necesarias", se deja de medir y se borran las cookies _ga.
	const desactivar = () => {
		window[`ga-disable-${id}`] = true;
		const dominio = location.hostname.replace(/^www\./, "");
		for (const par of document.cookie.split("; ")) {
			const nombre = par.split("=")[0];
			if (!nombre.startsWith("_ga")) continue;
			for (const sufijo of ["", `; Domain=${dominio}`, `; Domain=.${dominio}`]) {
				document.cookie = `${nombre}=; Max-Age=0; Path=/${sufijo}`;
			}
		}
	};

	if (window.hppAnaliticasAceptadas?.()) cargar();
	document.addEventListener("hpp:consentimiento", (evento) => {
		if (evento.detail === "aceptado") cargar();
		else desactivar();
	});
})();
