(function () {
  const form = document.getElementById("form-projeto-cw");
  const sucessoDiv = document.getElementById("sucesso");
  const sucessoMensagem = document.getElementById("sucesso-mensagem");
  const btnOutro = document.getElementById("btn-outro");
  const erroDiv = document.getElementById("erro");
  const erroMensagem = document.getElementById("erro-mensagem");
  const btnFecharErro = document.getElementById("btn-fechar-erro");
  const btnSubmit = document.getElementById("btn-submit");
  const blocoValorDireto = document.getElementById("bloco-valor-direto");
  const blocoLeiIncentivo = document.getElementById("bloco-lei-incentivo");
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

  function toggleInvestimento() {
    var sim = document.querySelector('input[name="lei_incentivo"][value="sim"]').checked;
    blocoValorDireto.hidden = sim;
    blocoLeiIncentivo.hidden = !sim;
  }

  document.querySelectorAll('input[name="lei_incentivo"]').forEach(function (radio) {
    radio.addEventListener("change", toggleInvestimento);
  });
  toggleInvestimento();

  function getCheckboxValues(name) {
    var nodes = document.querySelectorAll('input[name="' + name + '"]:checked');
    var arr = [];
    nodes.forEach(function (n) { arr.push(n.value); });
    return arr;
  }

  function fileToBase64(file) {
    return new Promise(function (resolve, reject) {
      if (!file || !file.size) {
        resolve("");
        return;
      }
      if (file.size > MAX_FILE_SIZE) {
        reject(new Error("Arquivo muito grande. Máximo 5 MB."));
        return;
      }
      var reader = new FileReader();
      reader.onload = function () {
        var base64 = reader.result.split(",")[1];
        resolve(base64 || "");
      };
      reader.onerror = function () { reject(new Error("Erro ao ler o arquivo.")); };
      reader.readAsDataURL(file);
    });
  }

  function showSuccess(data) {
    sucessoDiv.hidden = false;
    erroDiv.hidden = true;
    sucessoMensagem.textContent = data.message || "Seus dados foram recebidos. Nossa equipe verificará e entrará em contato se necessário.";
    sucessoDiv.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function showError(msg) {
    erroDiv.hidden = false;
    erroMensagem.textContent = msg;
    sucessoDiv.hidden = true;
    erroDiv.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  btnFecharErro.addEventListener("click", function () {
    erroDiv.hidden = true;
  });

  btnOutro.addEventListener("click", function () {
    sucessoDiv.hidden = true;
    form.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    var payload = {
      nome_organizacao: document.getElementById("nome_organizacao").value.trim(),
      cnpj: document.getElementById("cnpj").value.trim(),
      nome_responsavel: document.getElementById("nome_responsavel").value.trim(),
      cargo_funcao: document.getElementById("cargo_funcao").value.trim(),
      email: document.getElementById("email").value.trim(),
      celular_telefone: document.getElementById("celular_telefone").value.trim(),
      nome_projeto: document.getElementById("nome_projeto").value.trim(),
      area_focal: getCheckboxValues("area_focal"),
      publico_atendido: getCheckboxValues("publico_atendido"),
      local_estado: document.getElementById("local_estado").value.trim(),
      local_cidades: document.getElementById("local_cidades").value.trim(),
      objetivo_geral: document.getElementById("objetivo_geral").value.trim(),
      objetivo_1: document.getElementById("objetivo_1").value.trim(),
      resultado_1: document.getElementById("resultado_1").value.trim(),
      objetivo_2: document.getElementById("objetivo_2").value.trim(),
      resultado_2: document.getElementById("resultado_2").value.trim(),
      objetivo_3: document.getElementById("objetivo_3").value.trim(),
      resultado_3: document.getElementById("resultado_3").value.trim(),
      objetivo_4: document.getElementById("objetivo_4").value.trim(),
      resultado_4: document.getElementById("resultado_4").value.trim(),
      objetivo_5: document.getElementById("objetivo_5").value.trim(),
      resultado_5: document.getElementById("resultado_5").value.trim(),
      objetivo_6: document.getElementById("objetivo_6").value.trim(),
      resultado_6: document.getElementById("resultado_6").value.trim(),
      lei_incentivo: document.querySelector('input[name="lei_incentivo"][value="sim"]').checked,
      valor_direto: document.getElementById("valor_direto").value.trim(),
      leis: getCheckboxValues("leis"),
      valor_total_captacao: document.getElementById("valor_total_captacao").value.trim(),
      data_limite_captacao: document.getElementById("data_limite_captacao").value.trim(),
      certificado_base64: "",
      certificado_nome: "",
    };

    var fileInput = document.getElementById("certificado_file");
    var file = fileInput && fileInput.files && fileInput.files[0];

    btnSubmit.disabled = true;

    var send = function () {
      fetch("/api/submit-projeto-cw", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
        .then(function (res) {
          if (!res.ok) return res.json().then(function (d) { throw new Error(d.detail || res.statusText); });
          return res.json();
        })
        .then(showSuccess)
        .catch(function (err) {
          showError(err.message || "Erro ao enviar. Tente novamente.");
        })
        .finally(function () {
          btnSubmit.disabled = false;
        });
    };

    if (file) {
      fileToBase64(file)
        .then(function (base64) {
          payload.certificado_base64 = base64;
          payload.certificado_nome = file.name;
          send();
        })
        .catch(function (err) {
          showError(err.message || "Erro no arquivo.");
          btnSubmit.disabled = false;
        });
    } else {
      send();
    }
  });
})();
