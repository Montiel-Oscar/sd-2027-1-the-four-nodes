"use strict";
window.FourNodes = (() => {
  const key = "four-nodes-token";
  function token() { return sessionStorage.getItem(key); }
  function authHeaders() { return token() ? {Authorization: `Bearer ${token()}`} : {}; }
  function render() {
    const state = document.querySelector("#session-state");
    if (state) state.textContent = token() ? "Sesión iniciada" : "Inicia sesión para publicar y seguir municipios";
    const logout = document.querySelector("#logout");
    if (logout) logout.hidden = !token();
  }
  function setToken(value) {
    if (value) sessionStorage.setItem(key, value); else sessionStorage.removeItem(key);
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
  document.querySelector("#logout")?.addEventListener("click", () => setToken(null));
  const account = document.querySelector("#account-form");
  account?.addEventListener("submit", async event => {
    event.preventDefault();
    if (!account.reportValidity()) return;
    const buttons = [...account.querySelectorAll("button")];
    const status = document.querySelector("#account-status");
    buttons.forEach(button => { button.disabled = true; });
    status.textContent = "Procesando…";
    try {
      const credentials = {email:account.elements.email.value.trim(), password:account.elements.password.value};
      const action = event.submitter?.value === "register" ? "register" : "login";
      const data = await request(`/api/usuarios/${action}`, {method:"POST", body:JSON.stringify(credentials)});
      account.elements.password.value = "";
      if (action === "login") {
        setToken(data.access_token);
        status.textContent = "Sesión iniciada. Ya puedes publicar y seguir municipios.";
      } else status.textContent = "Cuenta creada. Inicia sesión con tus datos.";
    } catch (error) {
      status.textContent = error instanceof TypeError ? "No pudimos conectar. Reintenta en un momento." : error.message;
    } finally { buttons.forEach(button => { button.disabled = false; }); }
  });
  render();
  return {token, authHeaders, setToken, request};
})();
