import uuid
from datetime import date
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

        codigo = str(uuid.uuid4())[:8].upper()
        pdf_filename = f"doc_{codigo}.pdf"
        
        media_dir = Path(__file__).parent.parent.parent / "static" / "media" / "docs"
        media_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = media_dir / pdf_filename

        tipo = dados["tipo"]
        conteudo_extra = dados.get("conteudo", "")
        data_hoje = date.today().strftime('%d/%m/%Y')

        header_html = """
        <div style="text-align: center; font-family: Helvetica, sans-serif; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 18px;">CASA DE ORAÇÃO EVANGÉLICA DE TODOS OS POVOS</h1>
            <p style="margin: 5px 0; font-size: 12px;">Itajaí/SC</p>
            <hr style="border: 1px solid #ccc; margin-top: 10px;">
        </div>
        """

        footer_html = f"""
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
            <p style="margin-top: 20px; font-size: 9px; color: #555;">Código de Validação: {codigo}</p>
        </div>
        """

        body_html = ""

        if tipo == "recomendacao":
            body_html = f"""
            <p>À igreja do Senhor Jesus Cristo,</p>
            <p>A <b>Casa de Oração Evangélica de Todos os Povos</b> vem, por meio desta, RECOMENDAR o irmão(ã):</p>
            <p style="margin-left: 20px;"><b>Nome:</b> {pessoa.nome}</p>
            <p style="margin-left: 20px;"><b>CPF:</b> {pessoa.cpf or '____________________'}</p>
            <p>Declaramos que o referido irmão(ã) é membro fiel desta igreja, de bom testemunho cristão, conduta irrepreensível na vida familiar, social e ministerial, não havendo até a presente data nada que o desabone.</p>
            <p>Diante disso, o recomendamos para exercer a função de <b>{conteudo_extra or 'MEMBRO'}</b>, confiando que desempenhará seu ministério com zelo, sabedoria e temor ao Senhor, conforme as Sagradas Escrituras.</p>
            <p>Por ser verdade, firmamos a presente recomendação.</p>
            <p style="margin-top: 30px;">Itajaí – SC, {data_hoje}.</p>
            """
        elif tipo == "desligamento":
            body_html = f"""
            <p>À Diretoria e liderança da Casa de Oração Evangélica de Todos os Povos</p>
            <p>Eu, <b>{pessoa.nome}</b>, membro desta igreja, venho por meio desta carta solicitar formalmente meu desligamento do rol de membros da Igreja Casa de Oração Evangélica de Todos os Povos.</p>
            <p>Agradeço a Deus pela oportunidade de ter feito parte desta congregação e por todo o cuidado espiritual, ensinamentos e comunhão vivenciados durante o tempo em que permaneci neste ministério.</p>
            <p>Peço que meu nome seja retirado do rol de membros e dos registros administrativos da igreja. Ressalto que esta decisão foi tomada em oração e reflexão, com respeito à liderança e aos irmãos em Cristo.</p>
            <p>Continuarei orando por esta amada igreja, para que o Senhor continue abençoando o crescimento espiritual e missionário da obra.</p>
            <p>Sem mais para o momento, despeço-me fraternalmente.</p>
            <p style="margin-top: 30px;">Itajaí/SC, {data_hoje}.</p>
            <p style="margin-top: 40px; text-align: center;">Assinatura: _____________________________________</p>
            <p style="text-align: center;">Nome completo: {pessoa.nome}</p>
            <p style="text-align: center;">Telefone/Contato: {pessoa.telefone or '____________________'}</p>
            """
        elif tipo == "batismo":
            body_html = f"""
            <div style="text-align: center; margin-top: 50px;">
                <h2 style="font-size: 24px;">CERTIFICADO DE CONCLUSÃO</h2>
                <p style="margin-top: 30px; font-size: 14px;">A CASA DE ORAÇÃO EVANGÉLICA DE TODOS OS POVOS certifica que:</p>
                <h3 style="font-size: 20px; margin: 20px 0;">{pessoa.nome}</h3>
                <p>Concluiu o discipulado sobre <b>Batismo nas Águas</b>.</p>
                <p>Demonstrando compreensão dos princípios bíblicos e compromisso com a fé cristã.</p>
                <p style="margin-top: 40px;">Professor: Presbítero Salesio | Pastor Presidente: Cláudio da Silva</p>
                <p style="margin-top: 40px;">Assinatura: _____________________________________</p>
                <p>Data: {data_hoje}</p>
            </div>
            """
            footer_html = ""
        elif tipo == "cargo":
            body_html = f"""
            <p>Declaramos para os devidos fins que o(a) irmão(ã) <b>{pessoa.nome}</b>, portador(a) do CPF {pessoa.cpf or '____________________'}, foi separado(a) e empossado(a) no cargo de <b>{conteudo_extra or 'NOVO CARGO'}</b>.</p>
            <p>Que o Senhor o(a) abençoe nesta nova etapa de serviço e dedicação à Sua obra, concedendo sabedoria e graça para desempenhar o ministério com fidelidade.</p>
            <p style="margin-top: 30px;">Itajaí – SC, {data_hoje}.</p>
            """
        elif tipo == "membresia":
            body_html = f"""
            <h2 style="text-align: center; font-size: 22px; margin-bottom: 30px;">CARTA DE MEMBRESIA</h2>
            <p>Aos que esta carta lerem, graça e paz.</p>
            <p>Declaramos para os devidos fins que os irmãos:</p>
            <h3 style="text-align: center; margin: 20px 0;">{pessoa.nome}</h3>
            <p>foram recebidos como membros do Ministério Casa de Oração Evangélica de Todos os Povos, no dia {data_hoje}, passando a fazer parte desta congregação, com compromisso de comunhão, serviço, fé e crescimento espiritual na presença de Deus.</p>
            <p>Esta carta é emitida em reconhecimento à membresia dos irmãos junto ao ministério, de acordo com os princípios da Palavra de Deus e da comunhão cristã.</p>
            <p>Sem mais para o momento, declaramos nossa alegria em recebê-los como parte desta família de fé, desejando que o Senhor Jesus Cristo continue abençoando suas vidas.</p>
            <p style="margin-top: 30px; font-style: italic; text-align: center;">"Assim nós, que somos muitos, somos um só corpo em Cristo, mas individualmente somos membros uns dos outros." Romanos 12:5</p>
            <p style="margin-top: 30px;">Itajaí/SC, {data_hoje}.</p>
            """
        elif tipo == "mudanca":
            body_html = f"""
            <h2 style="text-align: center; font-size: 22px; margin-bottom: 30px;">CARTA DE MUDANÇA</h2>
            <p>À IGREJA CASA DE ORAÇÃO EVANGÉLICA DE TODOS OS POVOS</p>
            <p>Pela presente, certificamos que o(a) irmão(ã) <b>{pessoa.nome}</b>, portador(a) do CPF nº <b>{pessoa.cpf or '____________________'}</b>, membro em plena comunhão desta igreja, encontra-se em situação regular e desejando, por motivo de mudança ministerial, passar a congregar e servir a Deus junto à Casa de Oração Evangélica de Todos os Povos.</p>
            <p>Recomendamos o(a) referido(a) irmão(ã) com alegria e confiança, rogando ao Senhor que continue abençoando sua vida espiritual, familiar e ministerial nesta nova etapa de caminhada cristã.</p>
            <p>Que a graça e a paz de Cristo Jesus estejam sobre todos.</p>
            <p style="margin-top: 40px;">_____________________________________<br>Pastor Presidente</p>
            <p style="margin-top: 20px;">_____________________________________<br>Secretário(a)</p>
            """
            footer_html = ""
        elif tipo == "apresentacao":
            body_html = f"""
            <h2 style="text-align: center; font-size: 22px; margin-bottom: 30px;">APRESENTAÇÃO DE CRIANÇA</h2>
            <p>A paz do Senhor, igreja! Queridos irmãos e familiares, estamos reunidos diante de Deus para um momento muito especial: a apresentação da criança.</p>
            <p>Hoje, seus pais vêm à presença do Senhor e da igreja para agradecer pela vida desta criança e declarar o desejo de criá-la nos caminhos de Deus. Os filhos são herança do Senhor e uma bênção confiada aos cuidados da família.</p>
            <p><b>Leitura bíblica:</b> Marcos 10:14: "Deixai vir a mim os pequeninos e não os impeçais, porque dos tais é o Reino de Deus."</p>
            <p>Jesus demonstrou amor e cuidado pelas crianças. Ele as recebeu e as abençoou. Por isso, apresentamos esta criança ao Senhor em oração, reconhecendo o valor de sua vida e nossa necessidade da graça de Deus para cuidar dela.</p>
            <p><b>Oração de apresentação:</b> Senhor nosso Deus e Pai, nós Te agradecemos pela vida desta criança. Neste momento, nós a apresentamos diante de Ti e pedimos que a Tua mão esteja sobre ela todos os dias. Concede-lhe saúde, proteção, sabedoria e crescimento. Guarda seus passos e cerca sua vida com o Teu cuidado. Abençoa seus pais; dá-lhes amor, paciência, discernimento e força para educar sua filha segundo os Teus ensinamentos. Que nunca faltem neste lar a fé, a união, a oração e a Tua presença. Em nome de Jesus. Amém.</p>
            """
            footer_html = ""
        else:
            body_html = f"""
            <h2 style="text-align: center;">{dados['titulo'].upper()}</h2>
            <p><b>Nome:</b> {pessoa.nome}</p>
            <p>{conteudo_extra or 'Documento emitido pela igreja.'}</p>
            """

        html_completo = f"""
        <html>
        <head>
            <style>
                @page {{ size: a4; margin: 2cm; }}
                body {{ font-family: Helvetica, sans-serif; font-size: 12pt; line-height: 1.6; color: #000; }}
                p {{ margin-bottom: 10px; text-align: justify; }}
            </style>
        </head>
        <body>
            {header_html}
            {body_html}
            {footer_html}
        </body>
        </html>
        """

        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_completo, dest=pdf_file)
        
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
