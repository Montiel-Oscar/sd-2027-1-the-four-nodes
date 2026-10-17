"use strict";
const statusBox = document.querySelector("#status");
const form = document.querySelector("#publish-form");
let shareUrl = location.href;
const labels = {name:"Nombre",species:"Especie",traits:"Características",seen_at:"Fecha y hora",municipality:"Municipio",neighborhood:"Colonia",landmark:"Referencia",public_phone:"Teléfono",pet:"Mascota"};
function say(message) { statusBox.textContent = message; }
async function readResponse(response) {
  let data;
  try { data = await response.json(); } catch { throw new Error("El servidor no devolvió una respuesta válida. Intenta de nuevo."); }
  if (!response.ok) {
    if (Array.isArray(data.detail)) {
      throw new Error(data.detail.map(error => `${labels[error.loc?.at(-1)] || "Formulario"}: revisa el valor ingresado.`).join(" "));
    }
    const messages = {404:"No encontramos este reporte. Comprueba el enlace.",409:"Este intento tiene un conflicto. Revisa los datos antes de volver a publicar.",422:"Revisa los campos del formulario.",503:"El servicio no está disponible. Intenta de nuevo en un momento."};
    throw new Error(messages[response.status] || "No se pudo completar la solicitud. Intenta de nuevo.");
  }
  return data;
}
if (form) {
  let attempt = null;
  const consent = form.elements.show_phone;
  const phone = form.elements.public_phone;
  consent.addEventListener("change", () => { phone.disabled = !consent.checked; phone.required = consent.checked; });
  form.addEventListener("submit", async event => {
    event.preventDefault();
    for (const field of form.querySelectorAll("input:not([type=checkbox]),textarea")) {
      if (!field.disabled && field.type !== "datetime-local") field.value = field.value.trim();
    }
    if (!form.reportValidity()) return;
    const fields = form.elements;
    const payload = {
      pet: {name:fields.name.value,species:fields.species.value,traits:fields.traits.value},
      seen_at:new Date(fields.seen_at.value).toISOString(),
      municipality:fields.municipality.value,neighborhood:fields.neighborhood.value,landmark:fields.landmark.value,
      show_phone:consent.checked
    };
    if (consent.checked) payload.public_phone = phone.value;
    const body = JSON.stringify(payload);
    if (!attempt || attempt.body !== body) attempt = {body,key:crypto.randomUUID()};
    const button = form.querySelector("button[type=submit]");
    button.disabled = true;
    say("Publicando…");
    try {
      const data = await readResponse(await fetch("/api/reportes/extravios", {method:"POST",headers:{"Content-Type":"application/json","Idempotency-Key":attempt.key},body:attempt.body}));
      if (!data.id) throw new Error("La respuesta no incluye el identificador del reporte. Intenta de nuevo.");
      shareUrl = new URL(`/reportes/extravios/${encodeURIComponent(data.id)}`, location.origin).href;
      const link = document.querySelector("#public-link");
      link.href = shareUrl; link.textContent = shareUrl;
      document.querySelector("#success").hidden = false;
      form.hidden = true;
      say("");
      link.focus();
    } catch (error) {
      say(error instanceof TypeError ? "No pudimos conectar. Reintenta con los mismos datos; conservaremos la clave para evitar duplicados." : error.message);
      statusBox.focus();
    } finally { button.disabled = false; }
  });
} else {
  (async () => {
    try {
      const id = location.pathname.split("/").filter(Boolean).at(-1);
      const data = await readResponse(await fetch(`/api/reportes/extravios/${encodeURIComponent(id)}`));
      document.querySelector("#pet-name").textContent = `${data.pet.name} está en búsqueda`;
      document.title = `${data.pet.name} · Reporte de extravío`;
      document.querySelector("#pet-species").textContent = data.pet.species;
      document.querySelector("#pet-traits").textContent = data.pet.traits;
      const locationList = document.querySelector("#location");
      for (const [label,value] of [["Fecha y hora",new Date(data.seen_at).toLocaleString("es-MX",{dateStyle:"long",timeStyle:"short"})],["Municipio o alcaldía",data.municipality],["Colonia",data.neighborhood],["Referencia",data.landmark]]) {
        const term = document.createElement("dt"); term.textContent = label;
        const detail = document.createElement("dd"); detail.textContent = value;
        locationList.append(term,detail);
      }
      if (data.public_phone) {
        document.querySelector("#phone").textContent = data.public_phone;
        document.querySelector("#contact").hidden = false;
      }
      document.querySelector("#report").hidden = false;
      say("");
    } catch (error) { say(error instanceof TypeError ? "No pudimos cargar el reporte. Comprueba tu conexión y recarga la página." : error.message); }
  })();
}
document.querySelector("#copy-link").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(shareUrl); say("Enlace copiado."); }
  catch { say(`Copia este enlace: ${shareUrl}`); }
});
