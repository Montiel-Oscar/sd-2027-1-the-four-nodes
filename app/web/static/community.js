"use strict";
const api = window.FourNodes;
// El contrato local publica alertas en el puerto 8001.
const alertsOrigin = "http://localhost:8001";
const $ = selector => document.querySelector(selector);
function status(id, message) { $(id).textContent = message; }
function message(error) { return error instanceof TypeError ? "No pudimos conectar con el servicio. Reintenta; conservamos los datos del formulario." : error.message; }
function node(tag, text) { const element = document.createElement(tag); element.textContent = text; return element; }
function reportLink(kind, id, text) {
  const link = node("a", text);
  link.href = `/reportes/${kind}/${encodeURIComponent(id)}`;
  return link;
}
function wireForm(selector, statusId, handler) {
  const form = $(selector);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    for (const field of form.querySelectorAll("input,textarea")) {
      if (!["password","datetime-local","checkbox"].includes(field.type)) field.value = field.value.trim();
    }
    if (!form.reportValidity()) return;
    const buttons = [...form.querySelectorAll("button")];
    buttons.forEach(button => { button.disabled = true; });
    status(statusId, "Procesando…");
    try { await handler(form, event); }
    catch (error) { status(statusId, message(error)); }
    finally { buttons.forEach(button => { button.disabled = false; }); }
  });
}
let browseGeneration = 0;
async function browse(municipality = "") {
  const generation = ++browseGeneration;
  status("#browse-status", "Cargando reportes…");
  const results = await Promise.allSettled(["extravios", "hallazgos"].map(async kind => {
    const reports = await api.request(`/api/reportes/${kind}?${new URLSearchParams({municipality}).toString()}`);
    return {kind, reports};
  }));
  if (generation !== browseGeneration) return;
  $("#reports-list").replaceChildren();
  let count = 0;
  const failures = [];
  for (const result of results) {
    if (result.status === "rejected") { failures.push(message(result.reason)); continue; }
    const {kind, reports} = result.value;
    for (const report of reports) {
      const card = document.createElement("article");
      card.append(node("p", kind === "extravios" ? "Extravío" : "Hallazgo"), reportLink(kind, report.id, report.pet?.name || report.description), node("p", `${report.municipality} · ${report.neighborhood}`), node("p", new Date(report.seen_at).toLocaleString("es-MX")));
      $("#reports-list").append(card);
      count++;
    }
  }
  status("#browse-status", failures.length ? failures.join(" ") : count ? `${count} reportes encontrados.` : "No hay reportes para este municipio.");
}
wireForm("#filter-form", "#browse-status", async form => browse(form.elements.municipality.value));

let attempt = null;
const foundForm = $("#found-form");
foundForm.elements.show_phone.addEventListener("change", () => {
  foundForm.elements.public_phone.disabled = !foundForm.elements.show_phone.checked;
  foundForm.elements.public_phone.required = foundForm.elements.show_phone.checked;
});
foundForm.addEventListener("input", () => { $("#found-success").hidden = true; });
wireForm("#found-form", "#found-status", async form => {
  const f = form.elements;
  const payload = {description:f.description.value, seen_at:new Date(f.seen_at.value).toISOString(), municipality:f.municipality.value, neighborhood:f.neighborhood.value, landmark:f.landmark.value, show_phone:f.show_phone.checked};
  if (f.show_phone.checked) payload.public_phone = f.public_phone.value;
  const body = JSON.stringify(payload);
  // La API limita la clave por usuario; renovar el token no cambia el intento.
  if (!attempt || attempt.body !== body) attempt = {body, key:crypto.randomUUID()};
  const report = await api.request("/api/reportes/hallazgos", {private:true, method:"POST", headers:{"Idempotency-Key":attempt.key}, body:attempt.body});
  $("#found-link").href = `/reportes/hallazgos/${encodeURIComponent(report.id)}`;
  $("#found-success").hidden = false;
  status("#found-status", "Hallazgo publicado. Comparte su enlace.");
  $("#found-link").focus();
});

let sessionGeneration = 0;
let inboxBusy = false;
async function subscriptions() {
  const generation = sessionGeneration;
  if (!api.token()) return;
  try {
    const rows = await api.request(`${alertsOrigin}/api/alertas/subscriptions`, {private:true});
    if (generation !== sessionGeneration) return;
    $("#subscriptions").replaceChildren();
    for (const row of rows) {
      const item = node("li", `${row.municipality} `);
      const button = node("button", `Dejar de seguir ${row.municipality}`);
      button.type = "button";
      button.addEventListener("click", async () => {
        button.disabled = true;
        try {
          await api.request(`${alertsOrigin}/api/alertas/subscriptions/${encodeURIComponent(row.id)}`, {private:true, method:"DELETE"});
          if (generation === sessionGeneration) await subscriptions();
        } catch (error) { if (generation === sessionGeneration) status("#subscriptions-status", message(error)); }
        finally { button.disabled = false; }
      });
      item.append(button); $("#subscriptions").append(item);
    }
    status("#subscriptions-status", rows.length ? "Solo recibirás alertas de reportes nuevos." : "Todavía no sigues municipios.");
  } catch (error) { if (generation === sessionGeneration) status("#subscriptions-status", message(error)); }
}
wireForm("#subscription-form", "#subscriptions-status", async form => {
  await api.request(`${alertsOrigin}/api/alertas/subscriptions`, {private:true, method:"POST", body:JSON.stringify({municipality:form.elements.municipality.value})});
  await subscriptions();
});
async function inbox() {
  if (!api.token() || inboxBusy || document.hidden) return;
  const generation = sessionGeneration;
  inboxBusy = true;
  try {
    const rows = await api.request(`${alertsOrigin}/api/alertas/inbox`, {private:true});
    if (generation !== sessionGeneration) return;
    $("#inbox").replaceChildren();
    for (const row of rows) {
      // Solo se admiten rutas públicas del contrato, nunca URLs externas.
      const match = /^\/reportes\/(extravios|hallazgos)\/([0-9a-f-]{36})$/i.exec(row.public_url);
      if (!match) continue;
      const card = document.createElement("article");
      card.append(reportLink(match[1], match[2], `${row.type === "found_pet.reported" ? "Hallazgo" : "Extravío"} en ${row.municipality}`), node("p", new Date(row.created_at).toLocaleString("es-MX")));
      $("#inbox").append(card);
    }
    status("#inbox-status", rows.length ? "Bandeja actualizada." : "Tu bandeja está vacía. Aquí aparecerán los nuevos reportes de los municipios que sigues.");
  } catch (error) { if (generation === sessionGeneration) status("#inbox-status", message(error)); }
  finally { inboxBusy = false; }
}
function sessionChanged() {
  sessionGeneration++;
  $("#subscriptions").replaceChildren(); $("#inbox").replaceChildren();
  status("#subscriptions-status", api.token() ? "Cargando municipios…" : "Inicia sesión para seguir municipios.");
  status("#inbox-status", api.token() ? "Cargando bandeja…" : "Inicia sesión para consultar tus alertas.");
  subscriptions(); inbox();
}
window.addEventListener("sessionchange", sessionChanged);
$("#refresh-alerts").addEventListener("click", inbox);
document.addEventListener("visibilitychange", () => { if (!document.hidden) inbox(); });
setInterval(inbox, 30000);
sessionChanged();
browse();
