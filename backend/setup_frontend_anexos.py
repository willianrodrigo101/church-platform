"""Frontend de Anexos: componente reutilizavel + integracao no perfil da pessoa."""
import shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
FRONTEND_WEB = PROJETO / "frontend" / "web"
INDEX = FRONTEND_WEB / "index.html"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

print(f"Frontend: {FRONTEND_WEB}")

for b in FRONTEND_WEB.glob("index.html.bak.*"):
    b.unlink()
    print(f"  [DEL] {b.name}")

if INDEX.exists():
    backup = INDEX.with_suffix(f".html.bak.{STAMP}")
    shutil.copy2(INDEX, backup)
    print(f"[BACKUP] {backup.name}")

conteudo = INDEX.read_text(encoding="utf-8")

# ============================================================
# 1. CSS
# ============================================================
css = '''
  /* ============ ANEXOS ============ */
  .anexos-lista { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
  .anexo-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px;
    transition: all 0.15s;
  }
  .anexo-item:hover { border-color: var(--accent); }
  .anexo-icon {
    width: 40px; height: 40px;
    background: rgba(99,102,241,0.15);
    border-radius: 10px;
    display: grid; place-items: center;
    font-size: 18px; flex-shrink: 0;
    overflow: hidden;
  }
  .anexo-icon img {
    width: 100%; height: 100%; object-fit: cover;
    cursor: pointer;
  }
  .anexo-info { flex: 1; min-width: 0; }
  .anexo-nome {
    font-size: 13px; font-weight: 600;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .anexo-meta { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
  .anexo-acoes { display: flex; gap: 6px; flex-shrink: 0; }
  .anexo-btn {
    background: transparent; border: 1px solid var(--border);
    color: var(--text-muted); width: 32px; height: 32px;
    border-radius: 8px; cursor: pointer;
    display: grid; place-items: center;
    font-size: 14px; transition: all 0.15s;
  }
  .anexo-btn:hover { color: var(--text); border-color: var(--text-muted); }
  .anexo-btn.danger:hover { color: var(--danger); border-color: var(--danger); }

  .anexo-empty {
    padding: 20px; text-align: center;
    color: var(--text-muted); font-size: 13px;
    background: var(--bg); border: 1px dashed var(--border);
    border-radius: 10px;
    margin-top: 12px;
  }

  .anexo-secao {
    margin-top: 24px; padding-top: 20px;
    border-top: 1px solid var(--border);
  }
  .anexo-secao-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 12px;
  }
  .anexo-secao-titulo {
    font-size: 14px; font-weight: 700;
    display: flex; align-items: center; gap: 8px;
  }
  .anexo-upload-input { display: none; }
  .anexo-upload-label {
    padding: 8px 14px;
    background: var(--accent); color: white;
    border-radius: 8px; font-size: 12px; font-weight: 600;
    cursor: pointer; transition: all 0.15s;
    display: inline-flex; align-items: center; gap: 6px;
  }
  .anexo-upload-label:hover { background: var(--accent-hover); }

  .anexo-progress {
    height: 4px; background: var(--bg); border-radius: 999px;
    overflow: hidden; margin-top: 8px;
    display: none;
  }
  .anexo-progress.active { display: block; }
  .anexo-progress-fill {
    height: 100%; width: 0%;
    background: var(--accent);
    transition: width 0.3s ease;
  }

  /* Lightbox para imagem */
  .anexo-lightbox {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.9);
    display: none; place-items: center;
    z-index: 3000; padding: 40px;
    cursor: zoom-out;
  }
  .anexo-lightbox.active { display: grid; }
  .anexo-lightbox img {
    max-width: 90vw; max-height: 90vh;
    border-radius: 12px;
    box-shadow: 0 20px 80px rgba(0,0,0,0.6);
  }
'''

if ".anexos-lista" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. HTML: lightbox no final do body (antes de </body>)
# ============================================================
lightbox_html = '''
<div class="anexo-lightbox" id="anexo-lightbox" onclick="fecharLightbox()">
  <img id="anexo-lightbox-img" src="" alt="">
</div>
'''

if 'id="anexo-lightbox"' not in conteudo:
    conteudo = conteudo.replace('</body>', lightbox_html + '\n</body>', 1)

# ============================================================
# 3. JS
# ============================================================
js = '''
// ============ ANEXOS ============
const ICONES_TIPO = {
  "image/": "📷",
  "application/pdf": "📄",
  "application/msword": "📝",
  "application/vnd.openxmlformats-officedocument.wordprocessingml": "📝",
  "application/vnd.ms-excel": "📊",
  "application/vnd.openxmlformats-officedocument.spreadsheetml": "📊",
  "audio/": "🎵",
  "text/plain": "📃",
};

function iconAnexo(mime) {
  if (!mime) return "📎";
  for (const prefixo in ICONES_TIPO) {
    if (mime.startsWith(prefixo)) return ICONES_TIPO[prefixo];
  }
  return "📎";
}

function tamanhoHumano(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1024 / 1024).toFixed(1) + " MB";
}

function isImagem(mime) {
  return mime && mime.startsWith("image/");
}

async function listarAnexos(entidadeTipo, entidadeId) {
  try {
    const r = await apiFetch(`${API}/anexos/?entidade_tipo=${entidadeTipo}&entidade_id=${entidadeId}&limit=200`);
    if (!r.ok) return [];
    return await r.json();
  } catch (e) { return []; }
}

async function renderizarAnexos(containerId, entidadeTipo, entidadeId) {
  const div = document.getElementById(containerId);
  if (!div) return;

  div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-text">Carregando anexos...</div></div>`;

  const anexos = await listarAnexos(entidadeTipo, entidadeId);

  if (anexos.length === 0) {
    div.innerHTML = `<div class="anexo-empty">Nenhum anexo ainda.</div>`;
    return;
  }

  div.innerHTML = anexos.map(a => {
    const icon = iconAnexo(a.mime_type);
    const thumb = isImagem(a.mime_type)
      ? `<img src="${API}/anexos/${a.id}/download?token=${encodeURIComponent(getToken())}" alt="" onclick="event.stopPropagation(); abrirLightbox('${API}/anexos/${a.id}/download?token=${encodeURIComponent(getToken())}')">`
      : icon;
    const autor = a.enviado_por_usuario?.nome || "—";
    return `
      <div class="anexo-item">
        <div class="anexo-icon">${thumb}</div>
        <div class="anexo-info">
          <div class="anexo-nome">${a.nome_original}</div>
          <div class="anexo-meta">${tamanhoHumano(a.tamanho_bytes)} · ${autor} · ${new Date(a.created_at).toLocaleDateString("pt-BR")}</div>
        </div>
        <div class="anexo-acoes">
          <button class="anexo-btn" onclick="baixarAnexo('${a.id}')" title="Baixar">⬇</button>
          <button class="anexo-btn danger" onclick="deletarAnexo('${a.id}', '${containerId}', '${entidadeTipo}', '${entidadeId}')" title="Excluir">✕</button>
        </div>
      </div>
    `;
  }).join("");
}

async function uploadAnexo(entidadeTipo, entidadeId, inputEl, containerId) {
  const file = inputEl.files[0];
  if (!file) return;

  // Limite de 10 MB
  if (file.size > 10 * 1024 * 1024) {
    mostrarToast("❌ Arquivo maior que 10 MB", "error");
    inputEl.value = "";
    return;
  }

  const formData = new FormData();
  formData.append("arquivo", file);
  formData.append("entidade_tipo", entidadeTipo);
  formData.append("entidade_id", entidadeId);

  try {
    const r = await fetch(`${API}/anexos/upload`, {
      method: "POST",
      headers: { "Authorization": "Bearer " + getToken() },
      body: formData,
    });

    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail || "Erro no upload");
    }

    mostrarToast("✅ Arquivo anexado!", "success");
    inputEl.value = "";
    await renderizarAnexos(containerId, entidadeTipo, entidadeId);
  } catch (err) {
    mostrarToast("❌ " + err.message, "error");
    inputEl.value = "";
  }
}

function baixarAnexo(id) {
  const url = `${API}/anexos/${id}/download?token=${encodeURIComponent(getToken())}`;
  window.open(url, "_blank");
}

function abrirLightbox(url) {
  document.getElementById("anexo-lightbox-img").src = url;
  document.getElementById("anexo-lightbox").classList.add("active");
}

function fecharLightbox() {
  document.getElementById("anexo-lightbox").classList.remove("active");
}

async function deletarAnexo(id, containerId, entidadeTipo, entidadeId) {
  abrirConfirmar("Excluir anexo?", "Tem certeza? O arquivo será removido permanentemente.", async () => {
    try {
      const r = await apiFetch(`${API}/anexos/${id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.detail || "Erro");
      }
      mostrarToast("✅ Anexo removido.", "success");
      await renderizarAnexos(containerId, entidadeTipo, entidadeId);
    } catch (err) {
      mostrarToast("❌ " + err.message, "error");
    }
  });
}

// ============ INTEGRACAO NO PERFIL DA PESSOA ============
function renderizarSecaoAnexos(pessoaId) {
  return `
    <div class="anexo-secao">
      <div class="anexo-secao-header">
        <div class="anexo-secao-titulo">📎 Anexos</div>
        <label class="anexo-upload-label">
          + Anexar arquivo
          <input type="file" class="anexo-upload-input"
                 onchange="uploadAnexo('pessoa', '${pessoaId}', this, 'anexos-pessoa')">
        </label>
      </div>
      <div id="anexos-pessoa" class="anexos-lista"></div>
    </div>
  `;
}
'''

if "// ============ ANEXOS ============" not in conteudo:
    marcador = "// ============ ANIVERSARIANTES ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)

# ============================================================
# 4. Integrar no perfil da pessoa (aba Informacoes)
# ============================================================
# Substitui o final do renderizarCorpoPerfil (aba info) para adicionar anexos
old_info = '''    corpo.innerHTML = `<div class="info-grid">
      ${itens.map(([k,v]) => `<div class="info-item">
        <div class="info-item-label">${k}</div>
        <div class="info-item-valor">${v}</div>
      </div>`).join("")}
    </div>`;
    return;'''

new_info = '''    corpo.innerHTML = `<div class="info-grid">
      ${itens.map(([k,v]) => `<div class="info-item">
        <div class="info-item-label">${k}</div>
        <div class="info-item-valor">${v}</div>
      </div>`).join("")}
    </div>
    ${renderizarSecaoAnexos(p.id)}`;
    setTimeout(() => renderizarAnexos("anexos-pessoa", "pessoa", p.id), 50);
    return;'''

if old_info in conteudo and "renderizarSecaoAnexos(p.id)" not in conteudo:
    conteudo = conteudo.replace(old_info, new_info, 1)
    print("  [OK] Secao de anexos adicionada no perfil da pessoa")

# Suporte a token na URL para downloads diretos
# (o FastAPI não aceita token via query por padrão, mas vamos permitir)

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("Vá em Pessoas -> abrir perfil -> aba Informacoes.")
print("=" * 60)