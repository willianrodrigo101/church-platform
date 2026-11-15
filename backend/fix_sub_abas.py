"""Fix — adiciona sub-abas Certificados e Ferramentas na barra do Estudo."""
import re
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
INDEX = PROJETO / "frontend" / "web" / "index.html"

print(f"Alvo: {INDEX}")

c = INDEX.read_text(encoding="utf-8")

# 1. Verifica o que já existe
tem_cert = 'id="estudo-sub-certificados"' in c
tem_ferr = 'id="estudo-sub-ferramentas"' in c
tem_sub_cert = 'data-subtab="certificados"' in c
tem_sub_ferr = 'data-subtab="ferramentas"' in c

print(f"HTML Certificados existe:  {tem_cert}")
print(f"HTML Ferramentas existe:   {tem_ferr}")
print(f"Sub-aba Certificados:      {tem_sub_cert}")
print(f"Sub-aba Ferramentas:       {tem_sub_ferr}")
print()

# 2. Corrige a barra de sub-abas se ainda nao tem
if not tem_sub_cert:
    novo_bloco = '''      <div class="estudo-sub-abas">
        <button class="estudo-sub-aba ativa" data-subtab="catalogo" onclick="trocarSubAbaEstudo('catalogo')">📖 Catálogo</button>
        <button class="estudo-sub-aba" data-subtab="turmas" onclick="trocarSubAbaEstudo('turmas')">🎓 Turmas</button>
        <button class="estudo-sub-aba" data-subtab="quizzes" onclick="trocarSubAbaEstudo('quizzes')">📝 Quizzes</button>
        <button class="estudo-sub-aba" data-subtab="forum" onclick="trocarSubAbaEstudo('forum')">💬 Fórum</button>
        <button class="estudo-sub-aba" data-subtab="gamificacao" onclick="trocarSubAbaEstudo('gamificacao')">🏅 Gamificação</button>
        <button class="estudo-sub-aba" data-subtab="certificados" onclick="trocarSubAbaEstudo('certificados')">📜 Certificados</button>
        <button class="estudo-sub-aba" data-subtab="ferramentas" onclick="trocarSubAbaEstudo('ferramentas')">🔧 Ferramentas</button>
      </div>'''

    c2 = re.sub(r'<div class="estudo-sub-abas">.*?</div>', novo_bloco, c, count=1, flags=re.DOTALL)

    if c2 == c:
        print("[ERRO] Nao encontrei o bloco <div class=\"estudo-sub-abas\">.")
        print("       Me manda o trecho da barra de sub-abas do index.html.")
    else:
        c = c2
        INDEX.write_text(c, encoding="utf-8")
        print("[OK] Sub-abas corrigidas! (Certificados + Ferramentas adicionadas)")
else:
    print("[SKIP] Sub-abas ja existem")

# 3. Verifica se o resto esta tudo la
print()
if not tem_cert:
    print("[AVISO] HTML da sub-aba Certificados nao existe.")
    print("        Precisa rodar de novo: python .\\setup_frontend_estudo_bloco4.py")
elif not tem_ferr:
    print("[AVISO] HTML da sub-aba Ferramentas nao existe.")
else:
    print("[OK] HTML das sub-abas OK")

print()
print("=" * 60)
print("Agora faca Ctrl+Shift+R no navegador e teste.")
print("=" * 60)