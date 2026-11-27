"use strict";
(() => {
  const L = window.L;
  if (!L) return;
  const tiles = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
  const mexicoCity = [19.4326, -99.1332];
  const radiusMeters = 3000;

  function baseMap(element, options = {}) {
    const map = L.map(element, {scrollWheelZoom:false, ...options}).setView(mexicoCity, 12);
    L.tileLayer(tiles, {
      maxZoom:18,
      attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    return map;
  }
  function paint(map, latitude, longitude, existing) {
    if (existing) {
      existing.point.remove();
      existing.area.remove();
    }
    const position = [latitude, longitude];
    const area = L.circle(position, {radius:radiusMeters, color:"#b42318", weight:2, fillColor:"#e75445", fillOpacity:0.12}).addTo(map);
    const point = L.circleMarker(position, {radius:9, color:"#fff", weight:2, fillColor:"#b42318", fillOpacity:1}).addTo(map);
    return {point, area};
  }
  function picker(mapId, formId, locateId, statusId) {
    const element = document.getElementById(mapId);
    if (!element) return null;
    const form = document.getElementById(formId);
    const status = document.getElementById(statusId);
    const map = baseMap(element, {minZoom:3});
    let pin = null;
    map.on("click", ({latlng}) => {
      const latitude = Number(latlng.lat.toFixed(6));
      const longitude = Number(latlng.lng.toFixed(6));
      form.elements.latitude.value = String(latitude);
      form.elements.longitude.value = String(longitude);
      pin = paint(map, latitude, longitude, pin);
      status.textContent = `Punto marcado: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}. Radio de 3 km.`;
    });
    document.getElementById(locateId).addEventListener("click", () => {
      if (!navigator.geolocation) {
        status.textContent = "Este navegador no permite obtener tu ubicación. Mueve el mapa manualmente.";
        return;
      }
      status.textContent = "Buscando tu ubicación para centrar el mapa…";
      navigator.geolocation.getCurrentPosition(
        ({coords}) => {
          map.setView([coords.latitude, coords.longitude], 14);
          status.textContent = "Mapa centrado en tu ubicación. Haz clic en el lugar del reporte para marcarlo.";
        },
        () => { status.textContent = "No se pudo obtener tu ubicación. Mueve el mapa manualmente y haz clic."; },
        {timeout:10000, maximumAge:60000}
      );
    });
    return map;
  }

  const missing = picker("missing-map", "publish-form", "locate-missing", "missing-map-status");
  picker("found-map", "found-form", "locate-found", "found-map-status");
  document.addEventListener("wizardstep", event => {
    if (missing && event.detail === 1) setTimeout(() => missing.invalidateSize(), 0);
  });

  document.addEventListener("reportloaded", event => {
    const report = event.detail;
    if (!document.getElementById("report-map-section")) return;
    if (report.latitude == null || report.longitude == null) {
      document.getElementById("report-map-unavailable").hidden = false;
      return;
    }
    const section = document.getElementById("report-map-section");
    section.hidden = false;
    const map = baseMap("report-map", {minZoom:11, maxZoom:16});
    const pin = paint(map, report.latitude, report.longitude);
    map.fitBounds(pin.area.getBounds(), {padding:[20,20], maxZoom:14});
    setTimeout(() => map.invalidateSize(), 0);
  });
})();
