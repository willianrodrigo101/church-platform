"""Frontend do reset de senha: link no login, modal esqueci, tela reset,
botao trocar senha no perfil, botao resetar senha no admin."""
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
# 1. CSS adicional
# ============================================================
css = '''
  .link-esqueci {
    display: block; text-align: center;
    color: var(--text-muted); font-size: 13px;
    margin-top: 14px; cursor: pointer;
    transition: color 0.15s;
  }
  .link-esqueci:hover { color: var(--accent); }
  .token-box {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 14px;
    font-family: "Courier New", monospace;
    font-size: 12px; word-break: break-all;
    color: var(--accent); margin-top: 8px;
    user-select: all;
  }
  .alerta-info {
    background: rgba(99, 102, 241, 0.1);
    border-left: 3px solid var(--accent);
    padding: 12px 16px; border-radius: 8px;
    font-size: 13px; color: var(--text-muted);
    margin-bottom: 16px;
  }
'''

if ".link-esqueci" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Adicionar link "Esqueci minha senha" no form de login
# ============================================================
link_esqueci = '''<a class="link-esqueci" onclick="abrirEsqueciSenha()">Esqueceu a senha?</a>'''

if "link-esqueci" not in conteudo.split("</div>")[0] and 'onclick="abrirEsqueciSenha()"' not in conteudo:
    # Adiciona depois do botão Entrar
    marcador = '<div class="login-erro" id="login-erro"></div>'
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, marcador + "\n        " + link_esqueci, 1)

# ============================================================
# 3. Novos modais (esqueci senha, reset com token, trocar minha senha)
# ============================================================
modais = '''
<!-- Modal Esqueci Senha -->
<div class="modal-backdrop" id="modal-esqueci-senha">
  <div class="modal" style="max-width: 460px;">
    <div class="modal-header">
      <h2 class="modal-title">Esqueceu a senha?</h2>
      <button class="modal-close" onclick="fecharEsqueciSenha()">×</button>
    </div>
    <div class="alerta-info">
      Digite seu email. Vamos gerar um token de reset válido por 1 hora.
      <br><strong>Como não há envio de email configurado</strong>, peça o token ao administrador do sistema.
    </div>
    <form id="form-esqueci-senha" onsubmit="enviarEsqueciSenha(event)">
      <div class="form-group">
        <label class="form-label">Email</label>
        <input class="form-input" type="email" id="esqueci-email" required placeholder="seu@email.com">
      </div>
      <div id="esqueci-resultado" style="display:none;"></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharEsqueciSenha()">Fechar</button>
        <button type="submit" class="btn btn-primary" id="btn-esqueci">Gerar token</button>
      </div>
    </form>
  </div>
</div>

<!-- Modal Resetar com token -->
<div class="modal-backdrop" id="modal-resetar-token">
  <div class="modal" style="max-width: 460px;">
    <div class="modal-header">
      <h2 class="modal-title">Redefinir senha</h2>
      <button class="modal-close" onclick="fecharResetarToken()">×</button>
    </div>
    <form id="form-resetar-token" onsubmit="resetarComToken(event)">
      <div class="form-group">
        <label class="form-label">Token recebido</label>
        <input class="form-input" id="reset-token" required placeholder="Cole o token aqui">
      </div>
      <div class="form-group">
        <label class="form-label">Nova senha</label>
        <input class="form-input" type="password" id="reset-nova-senha" required minlength="6" placeholder="Mínimo 6 caracteres">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharResetarToken()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-reset-token">Redefinir</button>
      </div>
    </form>
  </div>
</div>

<!-- Modal Trocar Minha Senha -->
<div class="modal-backdrop" id="modal-trocar-senha">
  <div class="modal" style="max-width: 460px;">
    <div class="modal-header">
      <h2 class="modal-title">Alterar minha senha</h2>
      <button class="modal-close" onclick="fecharTrocarSenha()">×</button>
    </div>
    <form id="form-trocar-senha" onsubmit="trocarMinhaSenha(event)">
      <div class="form-group">
        <label class="form-label">Senha atual</label>
        <input class="form-input" type="password" id="trocar-atual" required placeholder="Sua senha atual">
      </div>
      <div class="form-group">
        <label class="form-label">Nova senha</label>
        <input class="form-input" type="password" id="trocar-nova" required minlength="6" placeholder="Mínimo 6 caracteres">
      </div>
      <div class="form-group">
        <label class="form-label">Confirmar nova senha</label>
        <input class="form-input" type="password" id="trocar-confirmar" required minlength="6" placeholder="Repita a nova senha">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharTrocarSenha()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-trocar-senha">Alterar senha</button>
      </div>
    </form>
  </div>
</div>

<!-- Modal Admin Resetar Senha de Outro -->
<div class="modal-backdrop" id="modal-admin-reset">
  <div class="modal" style="max-width: 460px;">
    <div class="modal-header">
      <h2 class="modal-title">Resetar senha do usuário</h2>
      <button class="modal-close" onclick="fecharAdminReset()">×</button>
    </div>
    <div class="alerta-info" id="admin-reset-info">Defina uma nova senha temporária. O usuário deve trocar depois.</div>
    <form id="form-admin-reset" onsubmit="adminResetarSenha(event)">
      <div class="form-group">
        <label class="form-label">Nova senha temporária</label>
        <input class="form-input" type="password" id="admin-reset-senha" required minlength="6" placeholder="Mínimo 6 caracteres">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharAdminReset()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-admin-reset">Resetar senha</button>
      </div>
    </form>
  </div>
</div>
'''

if 'id="modal-esqueci-senha"' not in conteudo:
    marcador = '<div class="modal-backdrop" id="modal-confirmar">'
    conteudo = conteudo.replace(marcador, modais + "\n" + marcador, 1)

# ============================================================
# 4. Botão "Alterar minha senha" no header (dropdown do usuário)
# ============================================================
# Vamos adicionar um pequeno botão ao lado do "Sair"
btn_alterar = '''<button class="btn-logout" onclick="abrirTrocarSenha()" style="margin-right:8px;">🔑 Senha</button>'''

if "abrirTrocarSenha()" not in conteudo.split("</header>")[0]:
    marcador = '<button class="btn-logout" onclick="fazerLogout()">Sair</button>'
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, btn_alterar + '\n      ' + marcador, 1)

# ============================================================
# 5. Botão "Resetar senha" no modal de detalhes do usuário
# ============================================================
if 'onclick="abrirAdminResetDoDetalhe()"' not in conteudo:
    # Adiciona botão dentro do modal-detalhes-usuario
    marcador = '<button class="btn btn-danger" onclick="confirmarDeletarUsuario()">Deletar</button>'
    if marcador in conteudo:
        conteudo = conteudo.replace(
            marcador,
            '<button class="btn btn-warning" onclick="abrirAdminResetDoDetalhe()">Resetar Senha</button>\n      ' + marcador,
            1,
        )

# ============================================================
# 6. JS
# ============================================================
js = '''
// ============ RESET DE SENHA ============

function abrirEsqueciSenha() {
  document.getElementById("form-esqueci-senha").reset();
  document.getElementById("esqueci-resultado").style.display = "none";
  document.getElementById("modal-esqueci-senha").classList.add("active");
  document.getElementById("esqueci-email").focus();
}
function fecharEsqueciSenha() {
  document.getElementById("modal-esqueci-senha").classList.remove("active");
}

async function enviarEsqueciSenha(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-esqueci");
  const resultado = document.getElementById("esqueci-resultado");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Gerando...";
  try {
    const r = await fetch(`${API}/auth/esqueci-senha`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: document.getElementById("esqueci-email").value.trim() }),
    });
    const d = await r.json();
    resultado.style.display = "block";
    if (d.token_debug) {
      resultado.innerHTML = `
        <div class="alerta-info" style="background:rgba(16,185,129,0.1); border-left-color:var(--success);">
          <strong>Token gerado (modo desenvolvimento):</strong>
          <div class="token-box">${d.token_debug}</div>
          <div style="margin-top:10px; font-size:12px;">
            Copie este token e use em "Redefinir senha" abaixo.
          </div>
          <button type="button" class="btn btn-primary" onclick="abrirResetarTokenComToken('${d.token_debug}')" style="margin-top:10px; width:100%;">
            Usar este token agora
          </button>
        </div>`;
    } else {
      resultado.innerHTML = `
        <div class="alerta-info">
          ${d.mensagem || "Se o email estiver cadastrado, um token foi gerado."}
          <br><br>Peça o token ao administrador do sistema.
        </div>`;
    }
  } catch (err) {
    mostrarToast("❌ " + err.message, "error");
  } finally {
    btn.disabled = false; btn.textContent = txt;
  }
}

function abrirResetarTokenComToken(token) {
  fecharEsqueciSenha();
  document.getElementById("form-resetar-token").reset();
  document.getElementById("reset-token").value = token;
  document.getElementById("modal-resetar-token").classList.add("active");
  document.getElementById("reset-nova-senha").focus();
}
function abrirResetarToken() {
  document.getElementById("form-resetar-token").reset();
  document.getElementById("modal-resetar-token").classList.add("active");
}
function fecharResetarToken() {
  document.getElementById("modal-resetar-token").classList.remove("active");
}

async function resetarComToken(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-reset-token");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Redefinindo...";
  try {
    const r = await fetch(`${API}/auth/resetar-senha`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        token: document.getElementById("reset-token").value.trim(),
        nova_senha: document.getElementById("reset-nova-senha").value,
      }),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || "Erro");
    fecharResetarToken();
    mostrarToast("✅ Senha redefinida! Faça login.", "success");
  } catch (err) {
    mostrarToast("❌ " + err.message, "error");
  } finally {
    btn.disabled = false; btn.textContent = txt;
  }
}

function abrirTrocarSenha() {
  document.getElementById("form-trocar-senha").reset();
  document.getElementById("modal-trocar-senha").classList.add("active");
  document.getElementById("trocar-atual").focus();
}
function fecharTrocarSenha() {
  document.getElementById("modal-trocar-senha").classList.remove("active");
}

async function trocarMinhaSenha(e) {
  e.preventDefault();
  const atual = document.getElementById("trocar-atual").value;
  const nova = document.getElementById("trocar-nova").value;
  const conf = document.getElementById("trocar-confirmar").value;
  if (nova !== conf) {
    mostrarToast("❌ As senhas não coincidem", "error");
    return;
  }
  const btn = document.getElementById("btn-trocar-senha");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Alterando...";
  try {
    const r = await apiFetch(`${API}/auth/me/senha`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ senha_atual: atual, nova_senha: nova }),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || "Erro");
    fecharTrocarSenha();
    mostrarToast("✅ Senha alterada com sucesso!", "success");
  } catch (err) {
    mostrarToast("❌ " + err.message, "error");
  } finally {
    btn.disabled = false; btn.textContent = txt;
  }
}

function abrirAdminResetDoDetalhe() {
  if (!usuarioAtual) return;
  document.getElementById("form-admin-reset").reset();
  document.getElementById("admin-reset-info").innerHTML =
    `Definir nova senha temporária para <strong>${usuarioAtual.nome}</strong>. ` +
    `O usuário deve trocar no próximo login.`;
  document.getElementById("modal-admin-reset").classList.add("active");
  document.getElementById("admin-reset-senha").focus();
}
function fecharAdminReset() {
  document.getElementById("modal-admin-reset").classList.remove("active");
}

async function adminResetarSenha(e) {
  e.preventDefault();
  if (!usuarioAtual) return;
  const btn = document.getElementById("btn-admin-reset");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Resetando...";
  try {
    const r = await apiFetch(`${API}/auth/usuarios/${usuarioAtual.id}/resetar-senha`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nova_senha: document.getElementById("admin-reset-senha").value }),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail || "Erro");
    fecharAdminReset();
    mostrarToast("✅ Senha resetada com sucesso!", "success");
  } catch (err) {
    mostrarToast("❌ " + err.message, "error");
  } finally {
    btn.disabled = false; btn.textContent = txt;
  }
}
'''

if "// ============ RESET DE SENHA ============" not in conteudo:
    marcador = "// ============ CONFIRMAR ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)

# Fecha o modal de detalhes do usuario ao abrir o modal de reset
conteudo = conteudo.replace(
    "function abrirAdminResetDoDetalhe() {",
    "function abrirAdminResetDoDetalhe() {\n  if (typeof fecharDetalhesUsuario === 'function') fecharDetalhesUsuario();",
    1,
)

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("=" * 60)