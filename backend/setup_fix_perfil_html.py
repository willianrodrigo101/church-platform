"""
setup_fix_perfil_html.py
------------------------
Adiciona cargo + data_filiacao na tela de perfil (frontend apenas).
"""
from pathlib import Path
import shutil
import io
import sys

BASE = Path(__file__).parent.resolve()
INDEX = BASE.parent / "frontend" / "web" / "index.html"
INDEX_BACKEND = BASE.parent / "backend" / "app" / "static" / "index.html"

shutil.copy2(INDEX, str(INDEX) + ".bak.perfil_html")
with open(INDEX, "r", encoding="utf-8", newline="") as f:
    html = f.read()

# 1. Badge de Cargo
ancora_tags = '''  tags.push(`<span class="card-tag ${p.membro ? 'membro' : 'visitante'}">${p.membro ? 'Membro' : 'Visitante'}</span>`);
  if (p.batizado) tags.push(`<span class="card-tag batizado">Batizado</span>`);'''

novo_tags = '''  if (p.cargo_eclesiastico) {
    const cargoClass = p.cargo_eclesiastico.toLowerCase().replace(/[\\s\\/]+/g, '-');
    tags.push(`<span class="cargo-badge ${cargoClass}">${p.cargo_eclesiastico}</span>`);
  }
  tags.push(`<span class="card-tag ${p.membro ? 'membro' : 'visitante'}">${p.membro ? 'Membro' : 'Visitante'}</span>`);
  if (p.batizado) tags.push(`<span class="card-tag batizado">Batizado</span>`);'''

if ancora_tags in html:
    html = html.replace(ancora_tags, novo_tags, 1)

# 2. Cargo e Filiação no Info Grid
ancora_itens = '''      ["CPF", p.cpf],
      ["Email", p.email],
      ["Telefone", p.telefone],
      ["Nascimento", p.data_nascimento ? new Date(p.data_nascimento + "T00:00:00").toLocaleDateString("pt-BR") : null],'''

novos_itens = '''      ["CPF", p.cpf],
      ["Email", p.email],
      ["Telefone", p.telefone],
      ["Nascimento", p.data_nascimento ? new Date(p.data_nascimento + "T00:00:00").toLocaleDateString("pt-BR") : null],
      ["Cargo Eclesiástico", p.cargo_eclesiastico],
      ["Data de Filiação", p.data_filiacao ? new Date(p.data_filiacao + "T00:00:00").toLocaleDateString("pt-BR") : null],'''

if ancora_itens in html:
    html = html.replace(ancora_itens, novos_itens, 1)

with io.open(INDEX, "w", encoding="utf-8", newline="") as f:
    f.write(html)

shutil.copy2(INDEX, INDEX_BACKEND)
print("[OK] Frontend atualizado e sincronizado.")