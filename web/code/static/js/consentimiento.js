// Aviso de cookies (#75). Guarda por separado el consentimiento de analítica y (#97)
// contenido externo; ambos se gestionan desde el mismo aviso.
(() => {
	const COOKIE_ANALITICA = "hpp_consentimiento";
	const COOKIE_CONTENIDO_EXTERNO = "hpp_contenido_externo";
	const UN_ANIO = 60 * 60 * 24 * 365;
	const aviso = document.getElementById("aviso-cookies");

	const leer = (nombre) => {
		const par = document.cookie
			.split("; ")
			.find((cookie) => cookie.startsWith(`${nombre}=`));
		return par ? par.slice(par.indexOf("=") + 1) : null;
	};

	window.hppAnaliticasAceptadas = () =>
		leer(COOKIE_ANALITICA) === "aceptado";
	window.hppContenidoExternoAceptado = () =>
		leer(COOKIE_CONTENIDO_EXTERNO) === "aceptado";

	if (!aviso) return;

	const guardar = (valor) => {
		const seguro = location.protocol === "https:" ? "; Secure" : "";
		for (const nombre of [COOKIE_ANALITICA, COOKIE_CONTENIDO_EXTERNO]) {
			document.cookie = `${nombre}=${valor}; Max-Age=${UN_ANIO}; Path=/; SameSite=Lax${seguro}`;
		}
		aviso.classList.add("d-none");
		document.dispatchEvent(
			new CustomEvent("hpp:consentimiento", { detail: valor })
		);
	};

	if (!leer(COOKIE_ANALITICA)) aviso.classList.remove("d-none");

	for (const boton of aviso.querySelectorAll("[data-consentimiento]")) {
		boton.addEventListener("click", () => guardar(boton.dataset.consentimiento));
	}
	for (const enlace of document.querySelectorAll("[data-abrir-aviso-cookies]")) {
		enlace.addEventListener("click", () => aviso.classList.remove("d-none"));
	}
})();
