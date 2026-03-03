(function () {
  const form = document.getElementById("form-pdf");
  const sucessoDiv = document.getElementById("sucesso");
  const sucessoMensagem = document.getElementById("sucesso-mensagem");
  const btnOutro = document.getElementById("btn-outro");
  const erroDiv = document.getElementById("erro");
  const erroMensagem = document.getElementById("erro-mensagem");
  const btnFecharErro = document.getElementById("btn-fechar-erro");
  const btnSubmit = document.getElementById("btn-submit");

  function showSuccess(data) {
    sucessoDiv.hidden = false;
    erroDiv.hidden = true;
    sucessoMensagem.textContent = data.message || "Seu projeto foi recebido e está em análise.";
    sucessoDiv.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function showError(msg) {
    erroDiv.hidden = false;
    erroMensagem.textContent = msg;
    sucessoDiv.hidden = true;
    erroDiv.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  btnFecharErro.addEventListener("click", function () { erroDiv.hidden = true; });
  btnOutro.addEventListener("click", function () {
    sucessoDiv.hidden = true;
    form.reset();
    form.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var fileInput = document.getElementById("pdf_file");
    var file = fileInput && fileInput.files && fileInput.files[0];
    if (!file) {
      showError("Selecione um arquivo PDF.");
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      showError("O arquivo é muito grande. Máximo 15 MB.");
      return;
    }
    var formData = new FormData();
    formData.append("pdf", file);
    formData.append("nome", document.getElementById("nome").value.trim());
    formData.append("email", document.getElementById("email").value.trim());

    btnSubmit.disabled = true;
    fetch("/api/submit-projeto-pdf", {
      method: "POST",
      body: formData,
      credentials: "same-origin",
    })
      .then(function (res) {
        if (!res.ok) return res.json().then(function (d) { throw new Error(d.detail || res.statusText); });
        return res.json();
      })
      .then(showSuccess)
      .catch(function (err) {
        showError(err.message || "Erro ao enviar. Tente novamente.");
      })
      .finally(function () { btnSubmit.disabled = false; });
  });
})();
