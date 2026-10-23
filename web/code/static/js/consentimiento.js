// Aviso de cookies (#75). Guarda la elección en la cookie hpp_consentimiento
// para que las analíticas (#58) solo se carguen si la persona las acepta:
// window.hppAnaliticasAceptadas() o el evento "hpp:consentimiento".
(() => {
	const COOKIE = "hpp_consentimiento";
	const UN_ANIO = 60 * 60 * 24 * 365;
	const aviso = document.getElementById("aviso-cookies");

	const leer = () => {
		const par = document.cookie
			.split("; ")
			.find((c) => c.startsWith(`${COOKIE}=`));
		return par ? par.split("=")[1] : null;
	};

	window.hppAnaliticasAceptadas = () => leer() === "aceptado";

	if (!aviso) return;

	const guardar = (valor) => {
		const seguro = location.protocol === "https:" ? "; Secure" : "";
		document.cookie = `${COOKIE}=${valor}; Max-Age=${UN_ANIO}; Path=/; SameSite=Lax${seguro}`;
		aviso.classList.add("d-none");
		document.dispatchEvent(
			new CustomEvent("hpp:consentimiento", { detail: valor })
		);
	};

	if (!leer()) aviso.classList.remove("d-none");

	for (const boton of aviso.querySelectorAll("[data-consentimiento]")) {
		boton.addEventListener("click", () => guardar(boton.dataset.consentimiento));
	}
	for (const enlace of document.querySelectorAll("[data-abrir-aviso-cookies]")) {
		enlace.addEventListener("click", () => aviso.classList.remove("d-none"));
	}
})();
