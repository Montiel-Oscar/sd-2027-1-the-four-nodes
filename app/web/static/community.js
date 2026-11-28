"use strict";
const api = window.FourNodes;
// Traefik dirige las rutas relativas al proceso de alertas.
const alertsOrigin = "";
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
      if (!["password","datetime-local","checkbox","file"].includes(field.type)) field.value = field.value.trim();
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
      card.className = "report-card";
      const preview = document.createElement("div");
      preview.className = "report-preview";
      const image = document.createElement("img");
      image.src = report.photo_url || (report.pet?.species === "gato" ? "/web/silhouette-cat.svg" : report.pet?.species === "perro" ? "/web/silhouette-dog.svg" : "/web/silhouette-paw.svg");
      image.alt = report.photo_url ? "Foto del reporte" : "Silueta de mascota; foto aún no disponible";
      image.loading = "lazy";
      preview.append(image);
      card.append(node("p", kind === "extravios" ? "Extravío" : "Hallazgo"), reportLink(kind, report.id, report.pet?.name || report.description), node("p", `${report.municipality} · ${report.neighborhood}`), node("p", new Date(report.seen_at).toLocaleString("es-MX")), preview);
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
  if (!f.latitude.value || !f.longitude.value) throw new Error("Haz clic en el mapa para marcar el lugar aproximado del hallazgo.");
  const payload = {description:f.description.value, seen_at:new Date(f.seen_at.value).toISOString(), municipality:f.municipality.value, neighborhood:f.neighborhood.value, landmark:f.landmark.value, latitude:Number(f.latitude.value), longitude:Number(f.longitude.value), show_phone:f.show_phone.checked};
  if (f.show_phone.checked) payload.public_phone = f.public_phone.value;
  const body = JSON.stringify(payload);
  // La API limita la clave por usuario; renovar el token no cambia el intento.
  if (!attempt || attempt.body !== body) attempt = {body, key:crypto.randomUUID()};
  const report = await api.request("/api/reportes/hallazgos", {private:true, method:"POST", headers:{"Idempotency-Key":attempt.key}, body:attempt.body});
  let photoWarning = "";
  try { await api.uploadPhoto("hallazgos", report.id, f.photo.files[0]); }
  catch (error) { photoWarning = ` El reporte quedó publicado, pero la foto no se guardó: ${error.message}`; }
  $("#found-link").href = `/reportes/hallazgos/${encodeURIComponent(report.id)}`;
  $("#found-success").hidden = false;
  status("#found-status", `Hallazgo publicado. Comparte su enlace.${photoWarning}`);
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
let activeConversation = null;
async function openConversation(id, title) {
  const generation = sessionGeneration;
  try {
    const rows = await api.request(`/api/reportes/conversaciones/${encodeURIComponent(id)}/mensajes`, {private:true});
    if (generation !== sessionGeneration) return;
    activeConversation = id;
    $("#conversation-thread").hidden = false;
    $("#thread-title").textContent = title;
    $("#thread-messages").replaceChildren();
    for (const row of rows) {
      const item = document.createElement("article");
      item.append(node("strong", row.sender_is_me ? "Tú" : "La otra persona"),
        node("p", row.body), node("small", new Date(row.created_at).toLocaleString("es-MX")));
      $("#thread-messages").append(item);
    }
    status("#reply-status", "");
  } catch (error) { if (generation === sessionGeneration) status("#messages-status", message(error)); }
}
async function conversations() {
  if (!api.token()) return;
  const generation = sessionGeneration;
  try {
    const rows = await api.request("/api/reportes/conversaciones", {private:true});
    if (generation !== sessionGeneration) return;
    $("#conversations-list").replaceChildren();
    for (const row of rows) {
      const card = document.createElement("article");
      const title = `${row.report_kind === "extravios" ? "Extravío" : "Hallazgo"}: ${row.report_title}`;
      const button = node("button", "Abrir conversación");
      button.type = "button";
      button.addEventListener("click", () => openConversation(row.id, title));
      card.append(reportLink(row.report_kind, row.report_id, title),
        node("p", `Participas como ${row.role}. Último mensaje: ${new Date(row.last_message_at).toLocaleString("es-MX")}`), button);
      $("#conversations-list").append(card);
    }
    status("#messages-status", rows.length ? `${rows.length} conversaciones. Abre una para leer y responder.` : "Todavía no tienes mensajes.");
    if (activeConversation && rows.some(row => row.id === activeConversation)) {
      const current = rows.find(row => row.id === activeConversation);
      await openConversation(activeConversation, `${current.report_kind === "extravios" ? "Extravío" : "Hallazgo"}: ${current.report_title}`);
    }
  } catch (error) { if (generation === sessionGeneration) status("#messages-status", message(error)); }
}
wireForm("#reply-form", "#reply-status", async form => {
  if (!activeConversation) throw new Error("Abre una conversación primero.");
  await api.request(`/api/reportes/conversaciones/${encodeURIComponent(activeConversation)}/mensajes`, {
    private:true, method:"POST", body:JSON.stringify({body:form.elements.body.value})
  });
  form.reset();
  await conversations();
  status("#reply-status", "Respuesta enviada.");
});
function sessionChanged() {
  sessionGeneration++;
  $("#subscriptions").replaceChildren(); $("#inbox").replaceChildren();
  activeConversation = null;
  $("#conversations-list").replaceChildren(); $("#thread-messages").replaceChildren();
  $("#conversation-thread").hidden = true;
  status("#messages-status", api.token() ? "Cargando conversaciones…" : "Inicia sesión para consultar tus mensajes.");
  status("#subscriptions-status", api.token() ? "Cargando municipios…" : "Inicia sesión para seguir municipios.");
  status("#inbox-status", api.token() ? "Cargando bandeja…" : "Inicia sesión para consultar tus alertas.");
  subscriptions(); inbox(); conversations();
}
window.addEventListener("sessionchange", sessionChanged);
$("#refresh-alerts").addEventListener("click", inbox);
$("#refresh-messages").addEventListener("click", conversations);
document.addEventListener("visibilitychange", () => { if (!document.hidden) { inbox(); conversations(); } });
setInterval(inbox, 30000);
setInterval(() => { if (!document.hidden) conversations(); }, 30000);
sessionChanged();
browse();
function showCommunitySection() {
  const section = location.hash.slice(1);
  const valid = ["overview", "pets", "browse", "found", "alerts", "messages"];
  const current = valid.includes(section) ? section : "overview";
  for (const panel of document.querySelectorAll(".community main > section")) panel.hidden = panel.id !== current;
  for (const link of document.querySelectorAll('.community .site-bar a[href^="#"]')) {
    link.classList.toggle("active", link.getAttribute("href") === `#${current}`);
  }
  const accountLink = document.querySelector(".community [data-login-link]");
  if (accountLink) accountLink.href = api.loginUrl(location.pathname + location.hash);
  if (current === "found") document.dispatchEvent(new Event("communitysectionchange"));
  if (current === "messages") conversations();
}
window.addEventListener("hashchange", showCommunitySection);
showCommunitySection();
