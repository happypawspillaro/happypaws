(() => {
	const embeds = [...document.querySelectorAll("[data-third-party-embed]")];

	const cargar = (embed) => {
		if (embed.querySelector("[data-third-party-frame]")) return;

		const src = embed.dataset.thirdPartySrc;
		if (!src) {
			console.error("Falta la URL del contenido externo.", embed);
			return;
		}

		const iframe = document.createElement("iframe");
		iframe.src = src;
		iframe.title = embed.dataset.thirdPartyTitle;
		iframe.loading = "lazy";
		iframe.referrerPolicy = "strict-origin-when-cross-origin";
		iframe.dataset.thirdPartyFrame = "";
		iframe.className = "border-0";
		if (embed.dataset.thirdPartyScrolling) {
			iframe.scrolling = embed.dataset.thirdPartyScrolling;
		}
		if (embed.dataset.thirdPartyAllow) {
			iframe.allow = embed.dataset.thirdPartyAllow;
		}

		const placeholder = embed.querySelector(".third-party-embed-placeholder");
		if (placeholder) placeholder.hidden = true;
		embed.append(iframe);
	};

	const descargar = (embed) => {
		embed.querySelector("[data-third-party-frame]")?.remove();
		const placeholder = embed.querySelector(".third-party-embed-placeholder");
		if (placeholder) placeholder.hidden = false;
	};

	const sincronizarConsentimiento = () => {
		const aceptado = window.hppContenidoExternoAceptado();
		for (const embed of embeds) {
			if (aceptado) cargar(embed);
			else descargar(embed);
		}
	};

	document.addEventListener("click", (evento) => {
		const enlace = evento.target.closest("[data-load-third-party]");
		const embed = enlace?.closest("[data-third-party-embed]");
		if (!embed) return;

		evento.preventDefault();
		cargar(embed);
	});

	document.addEventListener("hpp:consentimiento", sincronizarConsentimiento);
	sincronizarConsentimiento();
})();
