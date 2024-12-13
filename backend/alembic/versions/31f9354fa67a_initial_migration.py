"""Initial migration

Revision ID: 31f9354fa67a
Revises: 
Create Date: 2024-12-05 21:26:04.022534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '31f9354fa67a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('idiomas')
    op.drop_index('nombre', table_name='servicios')
    op.drop_table('servicios')
    op.drop_table('especialidad')
    op.drop_table('estudios')
    op.drop_table('grupo_edad')
    op.drop_table('tipos_parto')
    op.drop_index('expediente', table_name='expedientes')
    op.drop_index('hoja_emergencia', table_name='expedientes')
    op.drop_index('idx_expedientes_paciente', table_name='expedientes')
    op.drop_table('expedientes')
    op.drop_index('idx_uisau_consulta_id', table_name='uisau')
    op.drop_index('idx_uisau_estado_salud_id', table_name='uisau')
    op.drop_index('idx_uisau_lugar_referencia_id', table_name='uisau')
    op.drop_index('idx_uisau_parentesco_id', table_name='uisau')
    op.drop_index('idx_uisau_situacion_salud_id', table_name='uisau')
    op.drop_table('uisau')
    op.drop_index('idx_consultas_exp_id', table_name='consultas')
    op.drop_index('idx_consultas_fecha_consulta', table_name='consultas')
    op.drop_index('idx_consultas_medico', table_name='consultas')
    op.drop_index('idx_consultas_tipo_consulta', table_name='consultas')
    op.drop_table('consultas')
    op.drop_table('estados_salud')
    op.drop_index('dpi', table_name='usuarios')
    op.drop_index('username', table_name='usuarios')
    op.drop_table('usuarios')
    op.drop_table('depto_muni')
    op.drop_index('idx_madres_paciente', table_name='madres')
    op.drop_table('madres')
    op.drop_table('estadia_es')
    op.drop_table('servio_es')
    op.drop_table('estatus')
    op.drop_index('colegiado', table_name='medicos')
    op.drop_table('medicos')
    op.drop_table('nacionalidades')
    op.drop_index('nombre', table_name='roles')
    op.drop_table('roles')
    op.drop_table('codigo_procedimientos')
    op.drop_index('idx_recien_nacido_paciente', table_name='recien_nacidos')
    op.drop_table('recien_nacidos')
    op.drop_table('situaciones_salud')
    op.drop_index('nombre', table_name='permisos')
    op.drop_table('permisos')
    op.drop_index('nivel', table_name='educacion')
    op.drop_table('educacion')
    op.drop_table('parentescos')
    op.drop_index('idx_cie10_especialidad', table_name='cie10')
    op.drop_index('idx_cie10_grupo', table_name='cie10')
    op.drop_table('cie10')
    op.drop_index('idx_proce_medicos_codigo', table_name='proce_medicos')
    op.drop_index('idx_proce_medicos_especialidad', table_name='proce_medicos')
    op.drop_index('idx_proce_medicos_medico', table_name='proce_medicos')
    op.drop_index('idx_proce_medicos_servicio', table_name='proce_medicos')
    op.drop_table('proce_medicos')
    op.drop_index('doc', table_name='constancias_nacimiento')
    op.drop_index('idx_const_nac_madre', table_name='constancias_nacimiento')
    op.drop_index('idx_const_nac_medico', table_name='constancias_nacimiento')
    op.drop_index('idx_const_nac_recien_nacido', table_name='constancias_nacimiento')
    op.drop_table('constancias_nacimiento')
    op.drop_table('clases_parto')
    op.drop_table('tipo_citas')
    op.drop_index('idx_pacientes_educacion', table_name='pacientes')
    op.drop_index('idx_pacientes_estado_civil', table_name='pacientes')
    op.drop_index('idx_pacientes_idioma', table_name='pacientes')
    op.drop_index('idx_pacientes_lugar_nacimiento', table_name='pacientes')
    op.drop_index('idx_pacientes_nacionalidad_iso', table_name='pacientes')
    op.drop_index('idx_pacientes_pueblo', table_name='pacientes')
    op.drop_table('pacientes')
    op.drop_table('pueblos')
    op.drop_table('lugares_referencia')
    op.drop_index('nombre', table_name='tipo_lesion')
    op.drop_table('tipo_lesion')
    op.drop_table('referencia_contacto')
    op.drop_table('tipo_consulta')
    op.drop_index('idx_citas_especialidad', table_name='citas')
    op.drop_index('idx_citas_paciente_id', table_name='citas')
    op.drop_index('idx_citas_tipo_cita', table_name='citas')
    op.drop_table('citas')
    op.drop_index('nombre', table_name='estados_civiles')
    op.drop_table('estados_civiles')
    op.drop_table('contacto_paciente')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contacto_paciente',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('paciente_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('direccion', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('telefono1', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('telefono2', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('telefono3', mysql.VARCHAR(length=15), nullable=True),
    sa.Column('email', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], name='contacto_paciente_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('estados_civiles',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('nombre', 'estados_civiles', ['nombre'], unique=True)
    op.create_table('citas',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('paciente_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('especialidad', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('fecha_cita', sa.DATE(), nullable=True),
    sa.Column('tipo_cita', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('doble_fecha', mysql.ENUM('S', 'N'), server_default=sa.text("'N'"), nullable=True),
    sa.Column('laboratorio', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('fecha_laboratorio', sa.DATE(), nullable=True),
    sa.Column('nota', mysql.TEXT(), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('created_by', mysql.VARCHAR(length=8), nullable=True),
    sa.ForeignKeyConstraint(['especialidad'], ['especialidad.id'], name='citas_ibfk_2'),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], name='citas_ibfk_1', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tipo_cita'], ['tipo_citas.id'], name='citas_ibfk_3'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_citas_tipo_cita', 'citas', ['tipo_cita'], unique=False)
    op.create_index('idx_citas_paciente_id', 'citas', ['paciente_id'], unique=False)
    op.create_index('idx_citas_especialidad', 'citas', ['especialidad'], unique=False)
    op.create_table('tipo_consulta',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('descripcion', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('referencia_contacto',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('paciente_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('nombre_contacto', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('telefono_contacto', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('parentesco_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], name='referencia_contacto_ibfk_1'),
    sa.ForeignKeyConstraint(['parentesco_id'], ['parentescos.id'], name='referencia_contacto_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('tipo_lesion',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('descripcion', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('nombre', 'tipo_lesion', ['nombre'], unique=True)
    op.create_table('lugares_referencia',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('pueblos',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('pacientes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('apellido', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('dpi', mysql.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('pasaporte', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('sexo', mysql.ENUM('M', 'F'), server_default=sa.text("'M'"), nullable=True),
    sa.Column('nacimiento', sa.DATE(), nullable=True),
    sa.Column('defuncion', sa.DATE(), nullable=True),
    sa.Column('tiempo_defuncion', mysql.TIME(), nullable=True),
    sa.Column('nacionalidad_iso', mysql.VARCHAR(length=3), nullable=True),
    sa.Column('lugar_nacimiento', mysql.CHAR(length=4), nullable=True),
    sa.Column('estado_civil', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('educacion', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('pueblo', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('idioma', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ocupacion', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('estado', mysql.ENUM('V', 'M'), server_default=sa.text("'V'"), nullable=True),
    sa.Column('padre', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('madre', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('conyugue', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['educacion'], ['educacion.id'], name='pacientes_ibfk_4'),
    sa.ForeignKeyConstraint(['estado_civil'], ['estados_civiles.id'], name='pacientes_ibfk_3'),
    sa.ForeignKeyConstraint(['idioma'], ['idiomas.id'], name='pacientes_ibfk_6'),
    sa.ForeignKeyConstraint(['lugar_nacimiento'], ['depto_muni.codigo'], name='pacientes_ibfk_2'),
    sa.ForeignKeyConstraint(['nacionalidad_iso'], ['nacionalidades.iso'], name='pacientes_ibfk_1'),
    sa.ForeignKeyConstraint(['pueblo'], ['pueblos.id'], name='pacientes_ibfk_5'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_pacientes_pueblo', 'pacientes', ['pueblo'], unique=False)
    op.create_index('idx_pacientes_nacionalidad_iso', 'pacientes', ['nacionalidad_iso'], unique=False)
    op.create_index('idx_pacientes_lugar_nacimiento', 'pacientes', ['lugar_nacimiento'], unique=False)
    op.create_index('idx_pacientes_idioma', 'pacientes', ['idioma'], unique=False)
    op.create_index('idx_pacientes_estado_civil', 'pacientes', ['estado_civil'], unique=False)
    op.create_index('idx_pacientes_educacion', 'pacientes', ['educacion'], unique=False)
    op.create_table('tipo_citas',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('descripcion', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('clases_parto',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('descripcion', mysql.VARCHAR(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('constancias_nacimiento',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('fecha', sa.DATE(), nullable=False),
    sa.Column('doc', mysql.VARCHAR(length=15), nullable=True),
    sa.Column('madre_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('recien_nacido_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('medico', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['madre_id'], ['madres.id'], name='fk_const_nac_madre'),
    sa.ForeignKeyConstraint(['medico'], ['medicos.colegiado'], name='fk_const_nac_medico'),
    sa.ForeignKeyConstraint(['recien_nacido_id'], ['recien_nacidos.id'], name='fk_const_nac_recien_nacido'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='fk_const_nac_usuario'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_const_nac_recien_nacido', 'constancias_nacimiento', ['recien_nacido_id'], unique=False)
    op.create_index('idx_const_nac_medico', 'constancias_nacimiento', ['medico'], unique=False)
    op.create_index('idx_const_nac_madre', 'constancias_nacimiento', ['madre_id'], unique=False)
    op.create_index('doc', 'constancias_nacimiento', ['doc'], unique=True)
    op.create_table('proce_medicos',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('fecha', sa.DATE(), nullable=True),
    sa.Column('servicio_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('sexo', mysql.ENUM('M', 'F'), nullable=True),
    sa.Column('codigo_procedimiento_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('especialidad_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('cantidad', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('medico_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('grupo_edad', mysql.ENUM('N', 'A'), nullable=True),
    sa.Column('created_by', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['codigo_procedimiento_id'], ['codigo_procedimientos.id'], name='proce_medicos_ibfk_2'),
    sa.ForeignKeyConstraint(['especialidad_id'], ['especialidad.id'], name='proce_medicos_ibfk_3'),
    sa.ForeignKeyConstraint(['medico_id'], ['medicos.colegiado'], name='proce_medicos_ibfk_4'),
    sa.ForeignKeyConstraint(['servicio_id'], ['servicios.id'], name='proce_medicos_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_proce_medicos_servicio', 'proce_medicos', ['servicio_id'], unique=False)
    op.create_index('idx_proce_medicos_medico', 'proce_medicos', ['medico_id'], unique=False)
    op.create_index('idx_proce_medicos_especialidad', 'proce_medicos', ['especialidad_id'], unique=False)
    op.create_index('idx_proce_medicos_codigo', 'proce_medicos', ['codigo_procedimiento_id'], unique=False)
    op.create_table('cie10',
    sa.Column('cod', mysql.VARCHAR(length=7), nullable=False),
    sa.Column('grupo', mysql.CHAR(length=1), nullable=True),
    sa.Column('dx', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('abreviatura', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('especialidad_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['especialidad_id'], ['especialidad.id'], name='cie10_ibfk_1'),
    sa.PrimaryKeyConstraint('cod'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_cie10_grupo', 'cie10', ['grupo'], unique=False)
    op.create_index('idx_cie10_especialidad', 'cie10', ['especialidad_id'], unique=False)
    op.create_table('parentescos',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('educacion',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nivel', mysql.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('nivel', 'educacion', ['nivel'], unique=True)
    op.create_table('permisos',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('descripcion', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('nombre', 'permisos', ['nombre'], unique=True)
    op.create_table('situaciones_salud',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('recien_nacidos',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('paciente_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('hora', mysql.TIME(), nullable=True),
    sa.Column('peso_libras', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('peso_onzas', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('tipo_parto', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('clase_parto', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['clase_parto'], ['clases_parto.id'], name='recien_nacidos_ibfk_3'),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], name='recien_nacidos_ibfk_1'),
    sa.ForeignKeyConstraint(['tipo_parto'], ['tipos_parto.id'], name='recien_nacidos_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_recien_nacido_paciente', 'recien_nacidos', ['paciente_id'], unique=True)
    op.create_table('codigo_procedimientos',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('abreviatura', mysql.VARCHAR(length=10), nullable=False),
    sa.Column('procedimiento', mysql.VARCHAR(length=200), nullable=False),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('roles',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('descripcion', mysql.TEXT(), nullable=True),
    sa.Column('permisos', mysql.VARCHAR(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('nombre', 'roles', ['nombre'], unique=True)
    op.create_table('nacionalidades',
    sa.Column('iso', mysql.VARCHAR(length=3), nullable=False),
    sa.Column('nacionalidad', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('pais', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('cti', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('idioma', mysql.VARCHAR(length=30), nullable=True),
    sa.PrimaryKeyConstraint('iso'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('medicos',
    sa.Column('id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('colegiado', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=200), nullable=True),
    sa.Column('dpi', mysql.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('especialidad', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('pasaporte', mysql.VARCHAR(length=30), nullable=True),
    sa.Column('sexo', mysql.ENUM('M', 'F'), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['especialidad'], ['especialidad.id'], name='fk_medicos_especialidad'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('colegiado', 'medicos', ['colegiado'], unique=True)
    op.create_table('estatus',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('descripcion', mysql.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('servio_es',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('descripcion', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('estadia_es',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('descripcion', mysql.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('madres',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('paciente_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('vecindad', mysql.VARCHAR(length=4), nullable=True),
    sa.Column('hijos', mysql.INTEGER(), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('vivos', mysql.INTEGER(), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('muertos', mysql.INTEGER(), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('edad', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], name='madres_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_madres_paciente', 'madres', ['id'], unique=False)
    op.create_table('depto_muni',
    sa.Column('codigo', mysql.CHAR(length=4), nullable=False),
    sa.Column('departamento', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('municipio', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('lugar', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('codigo'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('usuarios',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=10), nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('dpi', mysql.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('contraseña', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('rol', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['rol'], ['roles.id'], name='usuarios_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('username', 'usuarios', ['username'], unique=True)
    op.create_index('dpi', 'usuarios', ['dpi'], unique=True)
    op.create_table('estados_salud',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('consultas',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('exp_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('fecha_consulta', sa.DATE(), nullable=True),
    sa.Column('hora', mysql.TIME(), nullable=True),
    sa.Column('fecha_recepcion', mysql.DATETIME(), nullable=True),
    sa.Column('fecha_egreso', mysql.DATETIME(), nullable=True),
    sa.Column('tipo_consulta', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('tipo_lesion', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('estancia', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('especialidad', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('servicio', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('fallecido', mysql.VARCHAR(length=1), nullable=True),
    sa.Column('referido', mysql.VARCHAR(length=1), nullable=True),
    sa.Column('contraindicado', mysql.VARCHAR(length=1), nullable=True),
    sa.Column('diagnostico', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('folios', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('medico', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('nota', mysql.TEXT(), nullable=True),
    sa.Column('estatus', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('lactancia', mysql.VARCHAR(length=1), nullable=True),
    sa.Column('prenatal', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('create_user', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('update_user', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('grupo_edad', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['especialidad'], ['especialidad.id'], name='consultas_ibfk_4'),
    sa.ForeignKeyConstraint(['estatus'], ['estatus.id'], name='consultas_ibfk_8'),
    sa.ForeignKeyConstraint(['exp_id'], ['expedientes.id'], name='consultas_ibfk_2'),
    sa.ForeignKeyConstraint(['grupo_edad'], ['grupo_edad.id'], name='consultas_ibfk_7'),
    sa.ForeignKeyConstraint(['medico'], ['medicos.colegiado'], name='consultas_ibfk_1'),
    sa.ForeignKeyConstraint(['servicio'], ['servicios.id'], name='consultas_ibfk_6'),
    sa.ForeignKeyConstraint(['tipo_consulta'], ['tipo_consulta.id'], name='consultas_ibfk_5'),
    sa.ForeignKeyConstraint(['tipo_lesion'], ['tipo_lesion.id'], name='consultas_ibfk_3'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_consultas_tipo_consulta', 'consultas', ['tipo_consulta'], unique=False)
    op.create_index('idx_consultas_medico', 'consultas', ['medico'], unique=False)
    op.create_index('idx_consultas_fecha_consulta', 'consultas', ['fecha_consulta'], unique=False)
    op.create_index('idx_consultas_exp_id', 'consultas', ['exp_id'], unique=False)
    op.create_table('uisau',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('consulta_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('estado_salud_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('situacion_salud_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('lugar_referencia_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('fecha_referencia', sa.DATE(), nullable=True),
    sa.Column('fecha_contacto', sa.DATE(), nullable=True),
    sa.Column('hora_contacto', mysql.TIME(), nullable=True),
    sa.Column('estadia', mysql.SMALLINT(), autoincrement=False, nullable=True),
    sa.Column('cama_numero', mysql.SMALLINT(), autoincrement=False, nullable=True),
    sa.Column('informacion', mysql.ENUM('S', 'N'), nullable=True),
    sa.Column('nombre_contacto', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('parentesco_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('telefono', mysql.VARCHAR(length=15), nullable=True),
    sa.Column('nota', mysql.TEXT(), nullable=True),
    sa.Column('estudios', mysql.VARCHAR(length=230), nullable=True),
    sa.Column('evolucion', mysql.TEXT(), nullable=True),
    sa.Column('recetado_por', mysql.ENUM('S', 'N'), nullable=True),
    sa.Column('shampoo', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('toalla', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('peine', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('jabon', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('cepillo_dientes', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('pasta_dental', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('sandalias', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('agua', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('papel', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('panales', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('created_by', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('update_by', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['consulta_id'], ['consultas.id'], name='uisau_ibfk_1', onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['estado_salud_id'], ['estados_salud.id'], name='uisau_ibfk_2'),
    sa.ForeignKeyConstraint(['lugar_referencia_id'], ['lugares_referencia.id'], name='uisau_ibfk_4'),
    sa.ForeignKeyConstraint(['parentesco_id'], ['parentescos.id'], name='uisau_ibfk_5'),
    sa.ForeignKeyConstraint(['situacion_salud_id'], ['situaciones_salud.id'], name='uisau_ibfk_3'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_uisau_situacion_salud_id', 'uisau', ['situacion_salud_id'], unique=False)
    op.create_index('idx_uisau_parentesco_id', 'uisau', ['parentesco_id'], unique=False)
    op.create_index('idx_uisau_lugar_referencia_id', 'uisau', ['lugar_referencia_id'], unique=False)
    op.create_index('idx_uisau_estado_salud_id', 'uisau', ['estado_salud_id'], unique=False)
    op.create_index('idx_uisau_consulta_id', 'uisau', ['consulta_id'], unique=False)
    op.create_table('expedientes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('paciente_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('expediente', mysql.VARCHAR(length=15), nullable=True),
    sa.Column('hoja_emergencia', mysql.VARCHAR(length=15), nullable=True),
    sa.Column('referencia_anterior', mysql.VARCHAR(length=11), nullable=True),
    sa.Column('expediente_madre', mysql.VARCHAR(length=11), nullable=True),
    sa.Column('created_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], name='expedientes_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('idx_expedientes_paciente', 'expedientes', ['id'], unique=False)
    op.create_index('hoja_emergencia', 'expedientes', ['hoja_emergencia'], unique=True)
    op.create_index('expediente', 'expedientes', ['expediente'], unique=True)
    op.create_table('tipos_parto',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('descripcion', mysql.VARCHAR(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('grupo_edad',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('grupo', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('edad_inicio', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('edad_fin', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('caracteristicas', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('estudios',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('descripcion', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('especialidad',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('especialista', mysql.VARCHAR(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('servicios',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('descripcion', mysql.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('nombre', 'servicios', ['nombre'], unique=True)
    op.create_table('idiomas',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', mysql.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###