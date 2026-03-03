(function () {
  const loading = document.getElementById("loading");
  const listWrap = document.getElementById("list-wrap");
  const empty = document.getElementById("empty");

  function scoreClass(p) {
    if (p >= 70) return "alta";
    if (p >= 40) return "media";
    return "baixa";
  }

  function formatDate(iso) {
    try {
      var d = new Date(iso);
      return d.toLocaleDateString("pt-BR", { dateStyle: "short" }) + " " + d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    } catch (_) {
      return iso;
    }
  }

  var labelsPT = {
    nome_organizacao: "Nome da organização",
    cnpj: "CNPJ",
    nome_responsavel: "Responsável",
    cargo_funcao: "Cargo/função",
    email: "E-mail",
    celular_telefone: "Celular/telefone",
    nome_projeto: "Nome do projeto",
    area_focal: "Área focal",
    publico_atendido: "Público atendido",
    local_estado: "Estado",
    local_cidades: "Cidades",
    objetivo_geral: "Objetivo geral",
    lei_incentivo: "Lei de incentivo",
    valor_direto: "Valor (aporte direto)",
    leis: "Leis",
    valor_total_captacao: "Valor total captação",
    data_limite_captacao: "Data limite captação",
    certificado: "Certificado (CAC/DO)",
  };

  function listItems(arr) {
    if (!arr || !arr.length) return "";
    return "<ul class='analise-list'>" + arr.map(function (x) { return "<li>" + escapeHtml(x) + "</li>"; }).join("") + "</ul>";
  }

  function renderProjetoCW(s) {
    var d = s.dados || {};
    var dataStr = formatDate(s.created_at);
    var nomeProjeto = d.nome_projeto || "—";
    var nomeOrg = d.nome_organizacao || "—";
    var resumo = s.resumo_ai || "";
    var prob = s.probabilidade_patrocinio;
    var hasAnalise = prob != null || (s.pontos_positivos && s.pontos_positivos.length) || (s.pontos_negativos && s.pontos_negativos.length) || (s.riscos && s.riscos.length);
    var probCl = prob != null ? scoreClass(prob) : "";
    var html = "<h3>" + escapeHtml(nomeProjeto) + " <span class='tipo-badge'>Projeto CW</span></h3>" +
      "<div class='submission-meta'>" + escapeHtml(nomeOrg) + " — Enviado em " + escapeHtml(dataStr) + "</div>";
    if (hasAnalise) {
      html += "<div class='analise-ia-block'>";
      if (prob != null) html += "<div class='submission-score " + probCl + "'>Probabilidade de patrocínio: " + prob + "%</div>";
      if (resumo) html += "<div class='submission-resumo'>" + escapeHtml(resumo) + "</div>";
      if (s.pontos_positivos && s.pontos_positivos.length) html += "<div class='analise-sec'><strong>Pontos positivos</strong>" + listItems(s.pontos_positivos) + "</div>";
      if (s.pontos_negativos && s.pontos_negativos.length) html += "<div class='analise-sec analise-neg'><strong>Pontos negativos</strong>" + listItems(s.pontos_negativos) + "</div>";
      if (s.riscos && s.riscos.length) html += "<div class='analise-sec analise-riscos'><strong>Riscos</strong>" + listItems(s.riscos) + "</div>";
      if (s.dados_faltantes && s.dados_faltantes.length) html += "<div class='analise-sec analise-faltantes'><strong>Dados que faltam para analisar melhor</strong>" + listItems(s.dados_faltantes) + "</div>";
      html += "</div>";
    } else if (resumo) {
      html += "<div class='submission-resumo'>" + escapeHtml(resumo) + "</div>";
    }
    html += "<details class='submission-details'><summary>Ver todos os dados do formulário</summary><div class='detail-sections'></div></details>";
    var el = document.createElement("div");
    el.className = "submission-item card submission-projeto-cw";
    el.innerHTML = html;
    var sections = el.querySelector(".detail-sections");
    if (sections && d) {
      var sect = function (tit, obj) {
        var rows = [];
        for (var k in obj) {
          if (obj[k] === "" || obj[k] == null || (Array.isArray(obj[k]) && obj[k].length === 0)) continue;
          var v = Array.isArray(obj[k]) ? obj[k].join(", ") : obj[k];
          if (typeof v === "boolean") v = v ? "Sim" : "Não";
          var label = labelsPT[k] || k;
          rows.push("<div class='detail-row'><span class='detail-key'>" + escapeHtml(label) + "</span><span class='detail-val'>" + escapeHtml(String(v)) + "</span></div>");
        }
        if (rows.length) sections.innerHTML += "<div class='detail-section'><h4>" + escapeHtml(tit) + "</h4>" + rows.join("") + "</div>";
      };
      sect("Institucional", {
        nome_organizacao: d.nome_organizacao,
        cnpj: d.cnpj,
        nome_responsavel: d.nome_responsavel,
        cargo_funcao: d.cargo_funcao,
        email: d.email,
        celular_telefone: d.celular_telefone,
      });
      sect("Projeto", {
        nome_projeto: d.nome_projeto,
        area_focal: d.area_focal,
        publico_atendido: d.publico_atendido,
        local_estado: d.local_estado,
        local_cidades: d.local_cidades,
      });
      var objObj = {};
      if (d.objetivo_geral) objObj.objetivo_geral = d.objetivo_geral;
      for (var i = 1; i <= 6; i++) {
        if (d["objetivo_" + i] || d["resultado_" + i]) objObj["Objetivo " + i] = (d["objetivo_" + i] || "") + (d["resultado_" + i] ? " — " + d["resultado_" + i] : "");
      }
      sect("Objetivos", objObj);
      var inv = {
        lei_incentivo: d.lei_incentivo,
        valor_direto: d.valor_direto,
        leis: d.leis,
        valor_total_captacao: d.valor_total_captacao,
        data_limite_captacao: d.data_limite_captacao,
      };
      if (d.certificado_path) inv.certificado = "Arquivo enviado";
      sect("Investimento", inv);
    }
    return el;
  }

  function renderProjetoPDF(s) {
    var d = s.dados || {};
    var dataStr = formatDate(s.created_at);
    var nome = d.nome_proponente || "—";
    var email = d.email_proponente || "";
    var pdfNome = d.pdf_nome || "PDF";
    var resumo = s.resumo_ai || "";
    var prob = s.probabilidade_patrocinio;
    var hasAnalise = prob != null || (s.pontos_positivos && s.pontos_positivos.length) || (s.pontos_negativos && s.pontos_negativos.length) || (s.riscos && s.riscos.length);
    var probCl = prob != null ? scoreClass(prob) : "";
    var html = "<h3>Projeto enviado em PDF <span class='tipo-badge'>PDF</span></h3>" +
      "<div class='submission-meta'>" + escapeHtml(pdfNome) + (email ? " — " + escapeHtml(email) : "") + " — Enviado em " + escapeHtml(dataStr) + "</div>";
    if (hasAnalise) {
      html += "<div class='analise-ia-block'>";
      if (prob != null) html += "<div class='submission-score " + probCl + "'>Probabilidade de patrocínio: " + prob + "%</div>";
      if (resumo) html += "<div class='submission-resumo'>" + escapeHtml(resumo) + "</div>";
      if (s.pontos_positivos && s.pontos_positivos.length) html += "<div class='analise-sec'><strong>Pontos positivos</strong>" + listItems(s.pontos_positivos) + "</div>";
      if (s.pontos_negativos && s.pontos_negativos.length) html += "<div class='analise-sec analise-neg'><strong>Pontos negativos</strong>" + listItems(s.pontos_negativos) + "</div>";
      if (s.riscos && s.riscos.length) html += "<div class='analise-sec analise-riscos'><strong>Riscos</strong>" + listItems(s.riscos) + "</div>";
      if (s.dados_faltantes && s.dados_faltantes.length) html += "<div class='analise-sec analise-faltantes'><strong>Dados que faltam para analisar melhor</strong>" + listItems(s.dados_faltantes) + "</div>";
      html += "</div>";
    } else if (resumo) {
      html += "<div class='submission-resumo'>" + escapeHtml(resumo) + "</div>";
    }
    return html;
  }

  function renderSubmission(s) {
    if (s.tipo === "projeto_pdf") {
      var el = document.createElement("div");
      el.className = "submission-item card submission-projeto-cw";
      el.innerHTML = renderProjetoPDF(s);
      return el;
    }
    if (s.tipo === "projeto_cw") return renderProjetoCW(s);
    var tipoLabel = s.tipo === "evento" ? "Evento" : "Projeto";
    var nome = (s.dados && s.dados.nome) ? s.dados.nome : "—";
    var score = s.pontuacao_patrocinio != null ? s.pontuacao_patrocinio : "—";
    var scoreCl = typeof score === "number" ? scoreClass(score) : "";
    var resumo = s.resumo_ai || "";
    var dataStr = formatDate(s.created_at);

    var el = document.createElement("div");
    el.className = "submission-item card";
    el.innerHTML =
      "<h3>" + escapeHtml(nome) + " <span style='color:var(--text-muted);font-weight:400;font-size:0.85em'>(" + tipoLabel + ")</span></h3>" +
      "<div class='submission-meta'>Enviado em " + escapeHtml(dataStr) + "</div>" +
      "<div class='submission-score " + scoreCl + "'>Potencial de patrocínio: " + (typeof score === "number" ? score + " / 100" : score) + "</div>" +
      (resumo ? "<div class='submission-resumo'>" + escapeHtml(resumo) + "</div>" : "");
    return el;
  }

  function escapeHtml(t) {
    var div = document.createElement("div");
    div.textContent = t;
    return div.innerHTML;
  }

  function load() {
    loading.hidden = false;
    listWrap.hidden = true;
    empty.hidden = true;

    fetch("/api/submissions")
      .then(function (res) { return res.json(); })
      .then(function (data) {
        loading.hidden = true;
        var list = (data && data.submissions) ? data.submissions : [];
        if (list.length === 0) {
          empty.hidden = false;
          return;
        }
        listWrap.innerHTML = "";
        list.forEach(function (s) {
          listWrap.appendChild(renderSubmission(s));
        });
        listWrap.hidden = false;
      })
      .catch(function () {
        loading.hidden = true;
        empty.hidden = false;
        empty.textContent = "Erro ao carregar. Verifique se está logado.";
      });
  }

  load();
})();
