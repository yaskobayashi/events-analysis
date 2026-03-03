(function () {
  const form = document.getElementById("form-login");
  const btnLogin = document.getElementById("btn-login");
  const loginErro = document.getElementById("login-erro");

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var username = document.getElementById("username").value.trim();
    var password = document.getElementById("password").value;

    loginErro.hidden = true;
    btnLogin.disabled = true;

    fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username, password: password }),
      credentials: "same-origin",
    })
      .then(function (res) {
        if (!res.ok) return res.json().then(function (d) { throw new Error(d.detail || "Credenciais inválidas."); });
        return res.json();
      })
      .then(function () {
        window.location.href = "/analises";
      })
      .catch(function (err) {
        loginErro.textContent = err.message || "Erro ao entrar. Tente novamente.";
        loginErro.hidden = false;
        btnLogin.disabled = false;
      });
  });
})();
