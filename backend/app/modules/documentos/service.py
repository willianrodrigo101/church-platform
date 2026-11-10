import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.documentos.models import Documento
from app.modules.pessoas.repository import PessoaRepository
from app.core.exceptions.handlers import BusinessRuleError

class DocumentoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pessoa_repo = PessoaRepository(db)

    async def gerar_documento(self, dados: dict, igreja_id: uuid.UUID, usuario_id: uuid.UUID):
        pessoa = await self.pessoa_repo.buscar_por_id(dados["pessoa_id"])
        if not pessoa:
            raise BusinessRuleError("Pessoa nao encontrada")

        # Gera codigo de validacao unico
        codigo = str(uuid.uuid4())[:8].upper()
        pdf_filename = f"doc_{codigo}.pdf"
        
        # Caminho onde o PDF sera salvo (pasta static/media)
        media_dir = Path(__file__).parent.parent.parent / "static" / "media" / "docs"
        media_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = media_dir / pdf_filename

        # --- GERACAO DO PDF BASICO ---
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4
        
        # Cabecalho
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2, height - 80, "IGREJA CASA DE ORACAO")
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 100, "Para Todos os Povos")
        
        # Titulo do Documento
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 160, dados["titulo"].upper())
        
        # Corpo (Simples por enquanto)
        c.setFont("Helvetica", 12)
        textobject = c.beginText(50, height - 200)
        textobject.textLine(f"Nome: {pessoa.nome}")
        textobject.textLine(f"Cargo: {pessoa.cargo_eclesiastico or 'Membro'}")
        textobject.textLine("")
        if dados.get("conteudo"):
            textobject.textLine(dados["conteudo"])
        
        c.drawText(textobject)
        
        # Rodape
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 50, f"Codigo de Validacao: {codigo}")
        c.drawString(50, 35, "Documento gerado eletronicamente pelo Church Platform")
        
        c.save()
        # -----------------------------

        doc = Documento(
            igreja_id=igreja_id,
            pessoa_id=pessoa.id,
            tipo=dados["tipo"],
            titulo=dados["titulo"],
            conteudo=dados.get("conteudo"),
            codigo_validacao=codigo,
            pdf_url=f"/static/media/docs/{pdf_filename}"
        )
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc
