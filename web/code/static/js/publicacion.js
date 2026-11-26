// Copia el texto de la publicación para redes (#39).
(() => {
	const texto = document.getElementById("texto-publicacion");
	const boton = document.getElementById("copiar-publicacion");
	const contador = document.getElementById("contador-publicacion");
	const aviso = document.getElementById("aviso-copiado");
	if (!texto || !boton) return;

	// Cuenta como Instagram: por caracteres, no por unidades UTF-16.
	const contar = () => {
		contador.textContent = [...texto.value].length;
	};
	texto.addEventListener("input", contar);
	contar();

	boton.addEventListener("click", async () => {
		try {
			await navigator.clipboard.writeText(texto.value);
			aviso.textContent = "¡Texto copiado!";
		} catch {
			texto.select();
			aviso.textContent = "Selecciona el texto y cópialo con Ctrl+C.";
		}
	});
})();
