"use strict";
window.FourNodes = (() => {
  const key = "four-nodes-token";
  const emailKey = "four-nodes-email";
  const token = () => sessionStorage.getItem(key);
  const email = () => sessionStorage.getItem(emailKey);
  const authHeaders = () => token() ? {Authorization:`Bearer ${token()}`} : {};
  function loginUrl(next = location.pathname + location.hash) {
    return `/cuenta?next=${encodeURIComponent(next)}`;
  }
  function render() {
    const state = document.querySelector("#session-state");
    if (state) {
      state.textContent = token() ? `Sesión activa${email() ? ` · ${email()}` : ""}` : "Aún no has iniciado sesión";
      state.classList.toggle("signed-in", Boolean(token()));
    }
    const logout = document.querySelector("#logout");
    if (logout) logout.hidden = !token();
    for (const link of document.querySelectorAll("[data-login-link]")) {
      link.href = loginUrl();
      link.textContent = token() ? "Mi cuenta" : "Iniciar sesión";
    }
  }
  function setToken(value, userEmail = null) {
    if (value) {
      sessionStorage.setItem(key, value);
      if (userEmail) sessionStorage.setItem(emailKey, userEmail);
    } else {
      sessionStorage.removeItem(key);
      sessionStorage.removeItem(emailKey);
    }
    render();
    window.dispatchEvent(new Event("sessionchange"));
  }
  async function request(url, {private: privateRequest = false, ...options} = {}) {
    if (privateRequest && !token()) throw new Error("Inicia sesión para continuar.");
    const response = await fetch(url, {...options, headers: {
      ...(options.body ? {"Content-Type":"application/json"} : {}),
      ...(privateRequest ? authHeaders() : {}), ...options.headers
    }});
    if (response.status === 401) {
      if (privateRequest) setToken(null);
      throw new Error(privateRequest ? "Tu sesión venció. Vuelve a entrar; tus datos se conservan." : "Correo o contraseña incorrectos.");
    }
    if (!response.ok) {
      const messages = {404:"No encontramos este recurso.",409:"Conflicto: el correo ya existe o la clave de publicación se reutilizó con otros datos.",422:"Revisa los campos y sus longitudes.",503:"Servicio temporalmente no disponible."};
      throw new Error(messages[response.status] || "No se pudo completar la solicitud.");
    }
    return response.status === 204 ? null : response.json();
  }
  async function uploadPhoto(kind, id, file) {
    if (!file) return;
    if (!token()) throw new Error("Inicia sesión para subir la foto.");
    if (!/\.jpe?g$/i.test(file.name) || file.type !== "image/jpeg") throw new Error("Selecciona un archivo JPG.");
    if (file.size > 3_000_000) throw new Error("La foto debe pesar menos de 3 MB.");
    const response = await fetch(`/api/reportes/${kind}/${encodeURIComponent(id)}/foto`, {
      method:"PUT", headers:{"Content-Type":"image/jpeg", ...authHeaders()}, body:file
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(typeof detail.detail === "string" ? detail.detail : "No se pudo subir la foto.");
    }
  }
  document.querySelector("#logout")?.addEventListener("click", () => setToken(null));
  const account = document.querySelector("#account-form");
  if (account) {
    const params = new URLSearchParams(location.search);
    const status = document.querySelector("#account-status");
    const title = document.querySelector("#auth-title");
    const submit = account.querySelector('[type="submit"]');
    const tabs = [...document.querySelectorAll("[data-auth-mode]")];
    const nextRaw = params.get("next") || "/comunidad";
    const destination = new URL(nextRaw, location.origin);
    const next = destination.origin === location.origin && destination.pathname !== "/cuenta" ? destination.pathname + destination.search + destination.hash : "/comunidad";
    let mode = "login";
    function showMode(value) {
      mode = value;
      title.textContent = value === "register" ? "Crea tu cuenta" : "Bienvenido de nuevo";
      submit.textContent = value === "register" ? "Crear cuenta" : "Iniciar sesión";
      account.elements.password.autocomplete = value === "register" ? "new-password" : "current-password";
      tabs.forEach(tab => tab.setAttribute("aria-selected", String(tab.dataset.authMode === value)));
      if (!params.has("registered")) status.textContent = "";
    }
    tabs.forEach(tab => tab.addEventListener("click", () => showMode(tab.dataset.authMode)));
    if (params.has("registered")) status.textContent = "Cuenta creada. Ahora inicia sesión con tu correo y contraseña.";
    account.addEventListener("submit", async event => {
      event.preventDefault();
      if (!account.reportValidity()) return;
      const credentials = {email:account.elements.email.value.trim(), password:account.elements.password.value};
      submit.disabled = true;
      status.textContent = mode === "register" ? "Creando tu cuenta…" : "Iniciando sesión…";
      try {
        const data = await request(`/api/usuarios/${mode}`, {method:"POST", body:JSON.stringify(credentials)});
        account.elements.password.value = "";
        if (mode === "register") {
          sessionStorage.setItem("four-nodes-pending-email", credentials.email);
          location.replace(`/cuenta?registered=1&next=${encodeURIComponent(next)}`);
        } else {
          setToken(data.access_token, credentials.email);
          sessionStorage.setItem("four-nodes-login-flash", `Sesión iniciada como ${credentials.email}`);
          location.assign(next);
        }
      } catch (error) {
        status.textContent = error instanceof TypeError ? "No pudimos conectar. Intenta de nuevo." : error.message;
      } finally { submit.disabled = false; }
    });
    const pending = sessionStorage.getItem("four-nodes-pending-email");
    if (pending) { account.elements.email.value = pending; sessionStorage.removeItem("four-nodes-pending-email"); }
    document.querySelector("#auth-return").href = next;
    if (token()) {
      document.querySelector("#already-signed-in").hidden = false;
      document.querySelector("#already-signed-in a").href = next;
    }
  }
  render();
  const flash = sessionStorage.getItem("four-nodes-login-flash");
  if (flash) {
    sessionStorage.removeItem("four-nodes-login-flash");
    const toast = document.createElement("p");
    toast.className = "session-toast";
    toast.setAttribute("role", "status");
    toast.textContent = flash;
    document.body.append(toast);
    setTimeout(() => toast.remove(), 5500);
  }
  return {token, email, authHeaders, setToken, request, uploadPhoto, loginUrl};
})();
