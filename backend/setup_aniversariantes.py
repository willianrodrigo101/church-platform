"""Adiciona endpoint de aniversariantes (hoje + proximos 7 dias)."""
import argparse, shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent

parser = argparse.ArgumentParser()
parser.add_argument("--force", action="store_true")
args = parser.parse_args()
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

def escrever(caminho: Path, conteudo: str):
    if caminho.exists():
        if not args.force:
            print(f"  [SKIP] {caminho.relative_to(PROJETO)}")
            return
        backup = caminho.with_suffix(caminho.suffix + f".bak.{STAMP}")
        shutil.copy2(caminho, backup)
        print(f"  [BACKUP] {backup.name}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    print(f"  [OK] {caminho.relative_to(PROJETO)}")


# ============================================================
# 1. Schemas adicionais para pessoas
# ============================================================
schemas_extra = '''

class Aniversariante(BaseModel):
    id: UUID
    nome: str
    data_nascimento: date
    idade: int
    dias_ate: int          # negativo = passou; 0 = hoje; positivo = futuro
    telefone: str | None = None
    email: str | None = None
    igreja_nome: str | None = None


class AniversariantesResumo(BaseModel):
    hoje: list[Aniversariante]
    proximos_7_dias: list[Aniversariante]
    ultimos_7_dias: list[Aniversariante]
    total_hoje: int
    total_semana: int
'''

# ============================================================
# 2. Repository: adiciona método de aniversariantes
# ============================================================
repo_metodo = '''

    async def aniversariantes(
        self,
        igreja_id: UUID | None = None,
        janela_dias: int = 7,
    ) -> list[dict]:
        """
        Retorna aniversariantes numa janela de +/- janela_dias em torno de hoje.
        Considera apenas mes/dia (ignora ano de nascimento).
        """
        from datetime import date, timedelta
        from sqlalchemy import extract, or_, and_

        hoje = date.today()
        mes_hoje = hoje.month
        dia_hoje = hoje.day

        # Calcula o intervalo [hoje - janela, hoje + janela]
        inicio = hoje - timedelta(days=janela_dias)
        fim = hoje + timedelta(days=janela_dias)

        # Extrai mes e dia como inteiros para comparacao
        mes = extract("month", Pessoa.data_nascimento)
        dia = extract("day", Pessoa.data_nascimento)

        # Monta filtro: pessoa cujo (mes, dia) esteja no intervalo
        # Como pode cruzar virada de mes/ano, vamos pegar todos os que tem data_nascimento
        # e filtrar em Python (mais simples e confiavel)

        stmt = select(Pessoa).where(
            Pessoa.ativo.is_(True),
            Pessoa.data_nascimento.is_not(None),
        )
        if igreja_id:
            stmt = stmt.where(Pessoa.igreja_id == igreja_id)

        r = await self.db.execute(stmt)
        pessoas = list(r.scalars().all())

        resultado = []
        for p in pessoas:
            dn = p.data_nascimento
            # Proximo aniversario neste ano
            try:
                aniv_este_ano = dn.replace(year=hoje.year)
            except ValueError:
                # 29 de fevereiro em ano nao bissexto -> 28 de fevereiro
                aniv_este_ano = dn.replace(year=hoje.year, day=28)

            # Se ja passou, considera o ano que vem
            if aniv_este_ano < hoje:
                try:
                    aniv_prox = dn.replace(year=hoje.year + 1)
                except ValueError:
                    aniv_prox = dn.replace(year=hoje.year + 1, day=28)
            else:
                aniv_prox = aniv_este_ano

            # Tambem considera o do ano passado, para "ultimos 7 dias"
            try:
                aniv_ant = dn.replace(year=hoje.year - 1)
            except ValueError:
                aniv_ant = dn.replace(year=hoje.year - 1, day=28)

            # Pega o mais relevante (mais proximo de hoje)
            candidatos = [aniv_ant, aniv_este_ano, aniv_prox]
            melhor = min(candidatos, key=lambda d: abs((d - hoje).days))
            dias_ate = (melhor - hoje).days

            if abs(dias_ate) <= janela_dias:
                idade = hoje.year - dn.year - ((hoje.month, hoje.day) < (dn.month, dn.day))
                resultado.append({
                    "id": p.id,
                    "nome": p.nome,
                    "data_nascimento": dn,
                    "idade": idade,
                    "dias_ate": dias_ate,
                    "telefone": p.telefone,
                    "email": p.email,
                    "igreja_id": p.igreja_id,
                    "igreja_nome": p.igreja.nome if p.igreja else None,
                })

        # Ordena: hoje primeiro, depois proximos, depois passados
        resultado.sort(key=lambda x: (abs(x["dias_ate"]), x["dias_ate"] < 0))
        return resultado
'''

# ============================================================
# 3. Router: adiciona endpoint
# ============================================================
router_extra = '''

@router.get("/aniversariantes/", response_model=AniversariantesResumo)
async def aniversariantes(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna aniversariantes de hoje, proximos 7 dias e ultimos 7 dias."""
    from app.modules.pessoas.schemas import Aniversariante
    from app.modules.pessoas.repository import PessoaRepository
    from app.modules.igreja.repository import IgrejaRepository

    if usuario.igreja_id and not igreja_id:
        igreja_id = usuario.igreja_id

    repo = PessoaRepository(db)
    lista = await repo.aniversariantes(igreja_id=igreja_id, janela_dias=7)

    hoje = [a for a in lista if a["dias_ate"] == 0]
    proximos = [a for a in lista if 0 < a["dias_ate"] <= 7]
    passados = [a for a in lista if -7 <= a["dias_ate"] < 0]

    def to_item(a):
        return Aniversariante(
            id=a["id"], nome=a["nome"], data_nascimento=a["data_nascimento"],
            idade=a["idade"], dias_ate=a["dias_ate"],
            telefone=a["telefone"], email=a["email"], igreja_nome=a["igreja_nome"],
        )

    return AniversariantesResumo(
        hoje=[to_item(a) for a in hoje],
        proximos_7_dias=[to_item(a) for a in proximos],
        ultimos_7_dias=[to_item(a) for a in passados],
        total_hoje=len(hoje),
        total_semana=len(proximos),
    )
'''


def atualizar_schemas():
    p = BACKEND / "app" / "modules" / "pessoas" / "schemas.py"
    if not p.exists():
        print(f"  [AVISO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class Aniversariante" in c:
        print("  [SKIP] schemas.py ja tem Aniversariante")
        return
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    c = c.rstrip() + schemas_extra
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] schemas.py atualizado")


def atualizar_repository():
    p = BACKEND / "app" / "modules" / "pessoas" / "repository.py"
    if not p.exists():
        print(f"  [AVISO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "async def aniversariantes" in c:
        print("  [SKIP] repository.py ja tem aniversariantes")
        return
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    # Insere o metodo no final da classe (antes do ultimo bloco de codigo)
    # Estrategia simples: adiciona no final do arquivo, indentado
    c = c.rstrip() + "\n" + repo_metodo
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] repository.py atualizado")


def atualizar_router():
    p = BACKEND / "app" / "modules" / "pessoas" / "router.py"
    if not p.exists():
        print(f"  [AVISO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "/aniversariantes/" in c:
        print("  [SKIP] router.py ja tem /aniversariantes/")
        return
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    c = c.rstrip() + "\n" + router_extra
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] router.py atualizado")


print(f"Backend: {BACKEND}")
print()

print("Adicionando suporte a aniversariantes...")
atualizar_schemas()
atualizar_repository()
atualizar_router()

print()
print("=" * 60)
print("PRONTO! Suba o uvicorn e teste:")
print("  GET /api/v1/pessoas/aniversariantes/")
print("=" * 60)