"use strict";
(() => {
  const api = window.FourNodes;
  const select = document.querySelector("#saved-pet");
  const form = document.querySelector("#pet-form");
  const list = document.querySelector("#pets-list");
  const status = document.querySelector("#pets-status");
  const reportForm = document.querySelector("#publish-form");
  let pets = [];
  let generation = 0;
  function say(text) { status.textContent = text; }
  function resetSelection() {
    if (!select) return;
    const previous = select.value;
    select.replaceChildren(new Option("Crear mascota junto con el reporte", ""));
    if (previous) {
      for (const name of ["name", "species", "traits"]) reportForm.elements[name].value = "";
    }
    syncSelection();
  }
  function syncSelection() {
    if (!select) return;
    const pet = pets.find(pet => pet.id === select.value);
    if (pet && ![...reportForm.elements.species.options].some(option => option.value === pet.species)) {
      reportForm.elements.species.add(new Option(pet.species, pet.species));
    }
    for (const name of ["name", "species", "traits"]) {
      const field = reportForm.elements[name];
      field.disabled = Boolean(pet);
      if (pet) field.value = pet[name];
    }
    reportForm.querySelectorAll("[data-species]").forEach(button => {
      button.disabled = Boolean(pet);
      button.setAttribute("aria-pressed", String(button.dataset.species === reportForm.elements.species.value));
    });
  }
  async function load() {
    const current = ++generation;
    const previousSelection = select?.value;
    pets = [];
    list?.replaceChildren();
    resetSelection();
    if (select) select.disabled = true;
    if (!api.token()) { say("Inicia sesión para ver tus fichas guardadas."); return; }
    say("Cargando tus mascotas…");
    try {
      const rows = await api.request("/api/mascotas", {private:true});
      if (current !== generation) return;
      pets = rows;
      for (const pet of pets) {
        select?.append(new Option(`${pet.name} · ${pet.species}`, pet.id));
        if (list) {
          const item = document.createElement("article");
          const title = document.createElement("h3"); title.textContent = pet.name;
          const details = document.createElement("p"); details.textContent = `${pet.species} · ${pet.traits}`;
          const link = document.createElement("a"); link.textContent = "Publicar extravío de esta mascota";
          link.href = `/?pet_id=${encodeURIComponent(pet.id)}#publish-form`;
          item.append(title, details, link); list.append(item);
        }
      }
      if (select) {
        select.disabled = false;
        const desired = previousSelection || new URLSearchParams(location.search).get("pet_id");
        if (pets.some(pet => pet.id === desired)) select.value = desired;
        syncSelection();
      }
      say(pets.length ? `${pets.length} fichas propias disponibles.` : "Todavía no tienes mascotas guardadas. Puedes registrar una sin publicar un reporte.");
    } catch (error) {
      if (current === generation) say(error instanceof TypeError ? "No pudimos cargar tus mascotas. Reintenta; puedes crear una junto con el reporte." : error.message);
    }
  }
  select?.addEventListener("change", syncSelection);
  document.querySelector("#refresh-pets")?.addEventListener("click", load);
  form?.addEventListener("submit", async event => {
    event.preventDefault();
    for (const field of form.querySelectorAll("input,textarea")) field.value = field.value.trim();
    if (!form.reportValidity()) return;
    const current = generation;
    const button = form.querySelector("button[type=submit]");
    button.disabled = true;
    say("Guardando ficha…");
    try {
      const f = form.elements;
      await api.request("/api/mascotas", {private:true, method:"POST", body:JSON.stringify({name:f.name.value, species:f.species.value, traits:f.traits.value})});
      if (current !== generation) return;
      form.reset();
      await load();
      say("Ficha guardada sin publicar ningún reporte. Ya puedes elegirla al crear un extravío.");
      status.focus();
    } catch (error) {
      if (current === generation) say(error instanceof TypeError ? "No pudimos confirmar si se guardó. Actualiza tus fichas antes de reintentar para evitar repetirla." : error.message);
    } finally { button.disabled = false; }
  });
  window.addEventListener("sessionchange", load);
  load();
})();
