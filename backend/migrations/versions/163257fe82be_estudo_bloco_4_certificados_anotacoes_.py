"""estudo bloco 4 certificados anotacoes ferramentas

Revision ID: 163257fe82be
Revises: 35d3fd0d4486
Create Date: 2026-10-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '163257fe82be'
down_revision: Union[str, None] = '35d3fd0d4486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============ certificados ============
    op.create_table(
        'certificados',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('matricula_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pessoa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('curso_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('igreja_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('codigo', sa.String(length=32), nullable=False),
        sa.Column('carga_horaria', sa.Integer(), nullable=True),
        sa.Column('nota_final', sa.Float(), nullable=True),
        sa.Column('emitido_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('url_pdf', sa.String(length=500), nullable=True),
        sa.Column('cancelado', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['matricula_id'], ['matriculas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pessoa_id'], ['pessoas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['curso_id'], ['cursos.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['igreja_id'], ['igrejas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('matricula_id', name='uq_certificados_matricula'),
        sa.UniqueConstraint('codigo', name='uq_certificados_codigo'),
    )
    op.create_index('ix_certificados_matricula_id', 'certificados', ['matricula_id'])
    op.create_index('ix_certificados_pessoa_id', 'certificados', ['pessoa_id'])
    op.create_index('ix_certificados_curso_id', 'certificados', ['curso_id'])
    op.create_index('ix_certificados_igreja_id', 'certificados', ['igreja_id'])
    op.create_index('ix_certificados_codigo', 'certificados', ['codigo'])

    # ============ anotacoes ============
    op.create_table(
        'anotacoes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pessoa_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('modulo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('igreja_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('conteudo', sa.Text(), nullable=False),
        sa.Column('favorito', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['pessoa_id'], ['pessoas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['modulo_id'], ['modulos_curso.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['igreja_id'], ['igrejas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_anotacoes_pessoa_id', 'anotacoes', ['pessoa_id'])
    op.create_index('ix_anotacoes_modulo_id', 'anotacoes', ['modulo_id'])
    op.create_index('ix_anotacoes_igreja_id', 'anotacoes', ['igreja_id'])

    # ============ ferramentas_estudo ============
    op.create_table(
        'ferramentas_estudo',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('igreja_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('categoria', sa.String(length=50), nullable=False, server_default='outro'),
        sa.Column('icone', sa.String(length=10), nullable=False, server_default='🔗'),
        sa.Column('ordem', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['igreja_id'], ['igrejas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ferramentas_estudo_igreja_id', 'ferramentas_estudo', ['igreja_id'])
    op.create_index('ix_ferramentas_estudo_categoria', 'ferramentas_estudo', ['categoria'])


def downgrade() -> None:
    op.drop_index('ix_ferramentas_estudo_categoria', table_name='ferramentas_estudo')
    op.drop_index('ix_ferramentas_estudo_igreja_id', table_name='ferramentas_estudo')
    op.drop_table('ferramentas_estudo')

    op.drop_index('ix_anotacoes_igreja_id', table_name='anotacoes')
    op.drop_index('ix_anotacoes_modulo_id', table_name='anotacoes')
    op.drop_index('ix_anotacoes_pessoa_id', table_name='anotacoes')
    op.drop_table('anotacoes')

    op.drop_index('ix_certificados_codigo', table_name='certificados')
    op.drop_index('ix_certificados_igreja_id', table_name='certificados')
    op.drop_index('ix_certificados_curso_id', table_name='certificados')
    op.drop_index('ix_certificados_pessoa_id', table_name='certificados')
    op.drop_index('ix_certificados_matricula_id', table_name='certificados')
    op.drop_table('certificados')