import uuid
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from xhtml2pdf import pisa
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
        
        # Caminho onde o PDF sera salvo
        media_dir = Path(__file__).parent.parent.parent / "static" / "media" / "docs"
        media_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = media_dir / pdf_filename

        # --- GERACAO DO HTML DO DOCUMENTO ---
        tipo = dados["tipo"]
        
        # Cabeçalho padrão
        header_html = """
        <div style="text-align: center; font-family: Helvetica, sans-serif; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 18px;">CASA DE ORAÇÃO EVANGÉLICA DE TODOS OS POVOS</h1>
            <p style="margin: 5px 0; font-size: 12px;">Itajaí/SC</p>
            <hr style="border: 1px solid #ccc; margin-top: 10px;">
        </div>
        """

        # Assinaturas padrão
        footer_html = """
        <div style="margin-top: 50px; text-align: center; font-family: Helvetica, sans-serif; font-size: 12px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="width: 50%; text-align: center;">
                        <p>_____________________________________<br><b>Pastor Cláudio da Silva</b><br>Pastor Presidente</p>
                    </td>
                    <td style="width: 50%; text-align: center;">
                        <p>_____________________________________<br><b>Pastora Marina da Silva</b><br>Pastora Fundadora</p>
                    </td>
                </tr>
                <tr>
                    <td colspan="2" style="text-align: center; padding-top: 20px;">
                        <p>_____________________________________<br><b>Presbítero Salesio Frainer</b><br>Secretário</p>
                    </td>
                </tr>
            </table>
        </div>
        """

        body_html = ""
        titulo_doc = dados["titulo"].upper()
        conteudo_extra = dados.get("conteudo", "")

        # MODELOS DE ACORDO COM O TIPO
        if tipo == "recomendacao":
            body_html = f"""
            <p>À igreja do Senhor Jesus Cristo,</p>
            <p>A <b>Casa de Oração Evangélica de Todos os Povos</b> vem, por meio desta, RECOMENDAR o irmão(ã):</p>
            <p><b>Nome:</b> {pessoa.nome}</p>
            <p><b>CPF:</b> {pessoa.cpf or '____________________'}</p>
            <p>Declaramos que o referido irmão(ã) é membro fiel desta igreja, de bom testemunho cristão, conduta irrepreensível na vida familiar, social e ministerial, não havendo até a presente data nada que o desabone.</p>
            <p>Diante disso, o recomendamos para exercer a função de <b>{conteudo_extra or 'MEMBRO'}</b>, confiando que desempenhará seu ministério com zelo, sabedoria e temor ao Senhor, conforme as Sagradas Escrituras.</p>
            <p>Por ser verdade, firmamos a presente recomendação.</p>
            <p style="margin-top: 30px;">Itajaí – SC, {__import__('datetime').date.today().strftime('%d/%m/%Y')}</p>
            """
            
        elif tipo == "desligamento":
            body_html = f"""
            <p>À Diretoria e liderança da Casa de Oração Evangélica de Todos os Povos</p>
            <p>Eu, <b>{pessoa.nome}</b>, membro desta igreja, venho por meio desta carta solicitar formalmente meu desligamento do rol de membros da Igreja Casa de Oração Evangélica de Todos os Povos.</p>
            <p>Agradeço a Deus pela oportunidade de ter feito parte desta congregação e por todo o cuidado espiritual, ensinamentos e comunhão vivenciados durante o tempo em que permaneci neste ministério.</p>
            <p>Peço que meu nome seja retirado do rol de membros e dos registros administrativos da igreja. Ressalto que esta decisão foi tomada em oração e reflexão, com respeito à liderança e aos irmãos em Cristo.</p>
            <p>Continuarei orando por esta amada igreja, para que o Senhor continue abençoando o crescimento espiritual e missionário da obra.</p>
            <p>Sem mais para o momento, despeço-me fraternalmente.</p>
            <p style="margin-top: 30px;">Itajaí/SC, {__import__('datetime').date.today().strftime('%d/%m/%Y')}.</p>
            <p style="margin-top: 40px;">Assinatura: _____________________________________</p>
            <p>Nome completo: {pessoa.nome}</p>
            <p>Telefone/Contato: {pessoa.telefone or '____________________'}</p>
            """
            
        elif tipo == "batismo":
            body_html = f"""
            <div style="text-align: center; margin-top: 50px;">
                <h2 style="font-size: 24px;">CERTIFICADO DE CONCLUSÃO</h2>
                <p style="margin-top: 30px; font-size: 14px;">A CASA DE ORAÇÃO EVANGÉLICA DE TODOS OS POVOS certifica que:</p>
                <h3 style="font-size: 20px; margin: 20px 0;">{pessoa.nome}</h3>
                <p>Concluiu o discipulado sobre <b>Batismo nas Águas</b>.</p>
                <p>Demonstrando compreensão dos princípios bíblicos e compromisso com a fé cristã.</p>
                <p style="margin-top: 30px;">Professor: Presbítero Salesio | Pastor Presidente: Cláudio da Silva</p>
                <p style="margin-top: 50px;">Assinatura: _____________________________________</p>
                <p>Data: ___ / ___ / _____</p>
            </div>
            """
            # Para certificado, geralmente não usamos o footer padrão grande
            footer_html = "" 
            
        elif tipo == "cargo":
            body_html = f"""
            <p>Declaramos para os devidos fins que o(a) irmão(ã) <b>{pessoa.nome}</b>, portador(a) do CPF {pessoa.cpf or '____________________'}, foi separado(a) e empossado(a) no cargo de <b>{conteudo_extra or 'NOVO CARGO'}</b>.</p>
            <p>Que o Senhor o(a) abençoe nesta nova etapa de serviço e dedicação à Sua obra, concedendo sabedoria e graça para desempenhar o ministério com fidelidade.</p>
            <p style="margin-top: 30px;">Itajaí – SC, {__import__('datetime').date.today().strftime('%d/%m/%Y')}</p>
            """
        else:
            # Fallback para documento genérico
            body_html = f"""
            <h2 style="text-align: center;">{titulo_doc}</h2>
            <p><b>Nome:</b> {pessoa.nome}</p>
            <p>{conteudo_extra or 'Documento emitido pela igreja.'}</p>
            """

        # HTML final completo
        html_completo = f"""
        <html>
        <head>
            <style>
                @page {{
                    size: a4;
                    margin: 2cm;
                }}
                body {{
                    font-family: Helvetica, sans-serif;
                    font-size: 12pt;
                    line-height: 1.6;
                    color: #000;
                }}
                p {{ margin-bottom: 10px; text-align: justify; }}
                h2 {{ text-align: center; }}
            </style>
        </head>
        <body>
            {header_html}
            {body_html}
            {footer_html}
        </body>
        </html>
        """

        # --- CONVERTE HTML PARA PDF ---
        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_completo,
                dest=pdf_file
            )
        
        if pisa_status.err:
            raise BusinessRuleError("Erro ao gerar o PDF.")

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