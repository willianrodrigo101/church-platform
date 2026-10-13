"""Integra Anexos nos modais de detalhes de Eventos, Cuidado, Oracao e Jornada."""
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
# 1. Adicionar <div> de anexos em cada modal de detalhes
# ============================================================

# Evento
marcador_evento = '''<div style="font-size:14px; font-weight:700; margin: 20px 0 12px;">Inscritos</div>
      <div id="detalhe-evento-inscritos"></div>'''

bloco_evento = '''<div style="font-size:14px; font-weight:700; margin: 20px 0 12px;">Inscritos</div>
      <div id="detalhe-evento-inscritos"></div>

      <div class="anexo-secao">
        <div class="anexo-secao-header">
          <div class="anexo-secao-titulo">📎 Anexos</div>
          <label class="anexo-upload-label">
            + Anexar arquivo
            <input type="file" class="anexo-upload-input"
                   onchange="uploadAnexoDeEvento(this)">
          </label>
        </div>
        <div id="anexos-evento" class="anexos-lista"></div>
      </div>'''

if 'id="anexos-evento"' not in conteudo and marcador_evento in conteudo:
    conteudo = conteudo.replace(marcador_evento, bloco_evento, 1)
    print("  [OK] Anexos adicionados no modal de Evento")

# Acompanhamento (cuidado)
marcador_acomp = '''<div id="detalhe-acomp-corpo"></div>
    <div class="modal-actions modal-actions-3">
      <button class="btn btn-ghost" onclick="fecharDetalhesAcomp()">Fechar</button>
      <button class="btn btn-primary" onclick="editarAcompDoDetalhe()">Editar</button>'''

bloco_acomp = '''<div id="detalhe-acomp-corpo"></div>

    <div class="anexo-secao">
      <div class="anexo-secao-header">
        <div class="anexo-secao-titulo">📎 Anexos</div>
        <label class="anexo-upload-label">
          + Anexar arquivo
          <input type="file" class="anexo-upload-input"
                 onchange="uploadAnexoDeAcomp(this)">
        </label>
      </div>
      <div id="anexos-acomp" class="anexos-lista"></div>
    </div>

    <div class="modal-actions modal-actions-3">
      <button class="btn btn-ghost" onclick="fecharDetalhesAcomp()">Fechar</button>
      <button class="btn btn-primary" onclick="editarAcompDoDetalhe()">Editar</button>'''

if 'id="anexos-acomp"' not in conteudo and marcador_acomp in conteudo:
    conteudo = conteudo.replace(marcador_acomp, bloco_acomp, 1)
    print("  [OK] Anexos adicionados no modal de Acompanhamento")

# Oracao
marcador_oracao = '''<div id="detalhe-oracao-corpo"></div>
    <div class="modal-actions modal-actions-3">
      <button class="btn btn-ghost" onclick="fecharDetalhesOracao()">Fechar</button>'''

bloco_oracao = '''<div id="detalhe-oracao-corpo"></div>

    <div class="anexo-secao">
      <div class="anexo-secao-header">
        <div class="anexo-secao-titulo">📎 Anexos</div>
        <label class="anexo-upload-label">
          + Anexar arquivo
          <input type="file" class="anexo-upload-input"
                 onchange="uploadAnexoDeOracao(this)">
        </label>
      </div>
      <div id="anexos-oracao" class="anexos-lista"></div>
    </div>

    <div class="modal-actions modal-actions-3">
      <button class="btn btn-ghost" onclick="fecharDetalhesOracao()">Fechar</button>'''

if 'id="anexos-oracao"' not in conteudo and marcador_oracao in conteudo:
    conteudo = conteudo.replace(marcador_oracao, bloco_oracao, 1)
    print("  [OK] Anexos adicionados no modal de Oracao")

# Trilha
marcador_trilha = '''<div style="font-size:14px; font-weight:700; margin: 20px 0 12px;">Etapas</div>
    <div id="detalhe-trilha-etapas"></div>'''

bloco_trilha = '''<div style="font-size:14px; font-weight:700; margin: 20px 0 12px;">Etapas</div>
    <div id="detalhe-trilha-etapas"></div>

    <div class="anexo-secao">
      <div class="anexo-secao-header">
        <div class="anexo-secao-titulo">📎 Anexos</div>
        <label class="anexo-upload-label">
          + Anexar arquivo
          <input type="file" class="anexo-upload-input"
                 onchange="uploadAnexoDeTrilha(this)">
        </label>
      </div>
      <div id="anexos-trilha" class="anexos-lista"></div>
    </div>'''

if 'id="anexos-trilha"' not in conteudo and marcador_trilha in conteudo:
    conteudo = conteudo.replace(marcador_trilha, bloco_trilha, 1)
    print("  [OK] Anexos adicionados no modal de Trilha")

# ============================================================
# 2. JS — funcoes de upload + hooks nos abridores de modal
# ============================================================
js = '''
// ============ ANEXOS — INTEGRACAO COM OUTROS MODULOS ============

// ---------- EVENTOS ----------
async function uploadAnexoDeEvento(inputEl) {
  if (!eventoAtual) return;
  await uploadAnexo("evento", eventoAtual.id, inputEl, "anexos-evento");
}

async function carregarAnexosDeEvento() {
  if (!eventoAtual) return;
  await renderizarAnexos("anexos-evento", "evento", eventoAtual.id);
}

// ---------- ACOMPANHAMENTO (CUIDADO) ----------
async function uploadAnexoDeAcomp(inputEl) {
  if (!acampAtual) return;
  await uploadAnexo("acompanhamento", acampAtual.id, inputEl, "anexos-acomp");
}

async function carregarAnexosDeAcomp() {
  if (!acampAtual) return;
  await renderizarAnexos("anexos-acomp", "acompanhamento", acampAtual.id);
}

// ---------- ORACAO ----------
async function uploadAnexoDeOracao(inputEl) {
  if (!oracaoAtual) return;
  await uploadAnexo("pedido_oracao", oracaoAtual.id, inputEl, "anexos-oracao");
}

async function carregarAnexosDeOracao() {
  if (!oracaoAtual) return;
  await renderizarAnexos("anexos-oracao", "pedido_oracao", oracaoAtual.id);
}

// ---------- TRILHA ----------
async function uploadAnexoDeTrilha(inputEl) {
  if (!trilhaAtual) return;
  await uploadAnexo("trilha", trilhaAtual.id, inputEl, "anexos-trilha");
}

async function carregarAnexosDeTrilha() {
  if (!trilhaAtual) return;
  await renderizarAnexos("anexos-trilha", "trilha", trilhaAtual.id);
}
'''

if "// ============ ANEXOS — INTEGRACAO COM OUTROS MODULOS ============" not in conteudo:
    marcador = "// ============ ANIVERSARIANTES ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)
        print("  [OK] Funcoes de upload/carregar adicionadas")

# ============================================================
# 3. Chamar carregarAnexosDeXXX nas funcoes de abrir modal
# ============================================================

# EVENTO
conteudo = conteudo.replace(
    "await carregarInscritos(id);\n}",
    "await carregarInscritos(id);\n  await carregarAnexosDeEvento();\n}",
    1,
)

# ACOMPANHAMENTO
conteudo = conteudo.replace(
    'document.getElementById("modal-detalhes-acomp").classList.add("active");\n}',
    'document.getElementById("modal-detalhes-acomp").classList.add("active");\n  carregarAnexosDeAcomp();\n}',
    1,
)

# ORACAO
conteudo = conteudo.replace(
    'document.getElementById("modal-detalhes-oracao").classList.add("active");\n}',
    'document.getElementById("modal-detalhes-oracao").classList.add("active");\n  carregarAnexosDeOracao();\n}',
    1,
)

# TRILHA
conteudo = conteudo.replace(
    'document.getElementById("modal-detalhes-trilha").classList.add("active");\n}',
    'document.getElementById("modal-detalhes-trilha").classList.add("active");\n  carregarAnexosDeTrilha();\n}',
    1,
)

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("Abra um evento, um acompanhamento, um pedido de oracao ou uma trilha.")
print("A secao de Anexos deve aparecer em cada um.")
print("=" * 60)