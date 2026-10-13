"""Fix — insere os blocos HTML de Certificados e Ferramentas."""
import re
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
INDEX = BACKEND.parent / "frontend" / "web" / "index.html"

print(f"Alvo: {INDEX}")

c = INDEX.read_text(encoding="utf-8")

# 1. Verifica se ja existe
if 'id="estudo-sub-certificados"' in c:
    print("[SKIP] HTML das sub-abas Certificados ja existe.")
    raise SystemExit(0)

# 2. Procura o bloco da gamificacao para inserir depois
# Pega o trecho desde <div id="estudo-sub-gamificacao" ate o fechamento do bloco
padrao_gam = r'(<div id="estudo-sub-gamificacao"[^>]*>.*?<div id="container-ranking"[^>]*></div>\s*</div>)'

match = re.search(padrao_gam, c, flags=re.DOTALL)
if not match:
    print("[ERRO] Nao encontrei o bloco de gamificacao.")
    print("       Me manda o trecho do index.html onde aparece:")
    print("         <div id=\"estudo-sub-gamificacao\"")
    raise SystemExit(1)

bloco_existente = match.group(1)

# 3. Cria os novos blocos HTML
novo_html = bloco_existente + '''

      <!-- SUB-ABA: CERTIFICADOS -->
      <div id="estudo-sub-certificados" style="display: none;">
        <div id="certificados-alertas" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px;"></div>

        <div class="toolbar" style="margin-bottom: 20px;">
          <button class="btn btn-primary" onclick="abrirFormEmitirCertificado()">🎓 Emitir Certificado</button>
          <button class="btn btn-success" onclick="abrirFormValidarCertificado()">✓ Validar Código</button>
          <div class="toolbar-count" id="contador-certificados"></div>
        </div>

        <div id="container-certificados" class="grid"></div>
      </div>

      <!-- SUB-ABA: FERRAMENTAS -->
      <div id="estudo-sub-ferramentas" style="display: none;">
        <div class="toolbar" style="margin-bottom: 20px;">
          <select class="toolbar-select" id="filtro-categoria-ferramenta" onchange="renderizarFerramentas()">
            <option value="">Todas as categorias</option>
            <option value="interlinear">Interlinear</option>
            <option value="lexico">Léxico</option>
            <option value="mapa">Mapa</option>
            <option value="gramatica">Gramática</option>
            <option value="comentario">Comentário</option>
            <option value="dicionario">Dicionário</option>
            <option value="referencia">Referência</option>
            <option value="outro">Outro</option>
          </select>
          <button class="btn btn-primary" onclick="abrirFormFerramenta()">+ Nova Ferramenta</button>
          <div class="toolbar-count" id="contador-ferramentas"></div>
        </div>

        <div id="container-ferramentas" class="grid"></div>
      </div>'''

# 4. Substitui
c = c.replace(bloco_existente, novo_html, 1)

INDEX.write_text(c, encoding="utf-8")
print("[OK] Blocos HTML de Certificados e Ferramentas inseridos!")
print()
print("Agora faca Ctrl+Shift+R no navegador e teste.")