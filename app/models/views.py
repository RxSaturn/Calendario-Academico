from app import db
from sqlalchemy import inspect

# Verificar o tipo de banco de dados
def is_sqlite():
    """Verifica se o banco de dados atual é SQLite"""
    try:
        engine_name = db.engine.name
        return engine_name == 'sqlite'
    except:
        # Fallback para SQLite em caso de erro
        return True

class EventosAtivosHoje(db.Model):
    __tablename__ = 'vw_eventos_ativos_hoje'
    __table_args__ = {'info': {'is_view': True}}
    
    id_evento = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    descricao = db.Column(db.String)
    datainicio = db.Column(db.Date)
    datafim = db.Column(db.Date)
    local = db.Column(db.String)
    categoria = db.Column(db.String)


class ResumoCalendario(db.Model):
    __tablename__ = 'vw_resumo_calendario'
    __table_args__ = {'info': {'is_view': True}}
    
    id_calendario = db.Column(db.Integer, primary_key=True)
    nomecalendario = db.Column(db.String)
    ano = db.Column(db.Integer)
    datainicio = db.Column(db.Date)
    datafim = db.Column(db.Date)
    ativo = db.Column(db.Boolean)
    tipocalendario = db.Column(db.String)
    totalcategorias = db.Column(db.Integer)
    totaleventos = db.Column(db.Integer)


class EventosFuturosAtivos(db.Model):
    __tablename__ = 'vw_eventos_futuros_ativos'
    __table_args__ = {'info': {'is_view': True}}
    
    id_evento = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    datainicio = db.Column(db.Date)
    datafim = db.Column(db.Date)
    calendario = db.Column(db.String)
    categoria = db.Column(db.String)

# Estas views só serão carregadas se estiver usando PostgreSQL
if not is_sqlite():
    class DiasLetivos(db.Model):
        __tablename__ = 'vw_dias_letivos'
        __table_args__ = {'info': {'is_view': True}}
        
        periodo = db.Column(db.String, primary_key=True)
        calendario = db.Column(db.String, primary_key=True)
        categoria = db.Column(db.String, primary_key=True)
        dias_planejados = db.Column(db.Integer)
        dias_com_eventos = db.Column(db.Integer)
        eventos_ultimos_30_dias = db.Column(db.Integer)


    class FeriadosDiasLetivos(db.Model):
        __tablename__ = 'vw_feriados_dias_letivos'
        __table_args__ = {'info': {'is_view': True}}
        
        feriado = db.Column(db.String, primary_key=True)
        data = db.Column(db.Date, primary_key=True)
        dia_semana = db.Column(db.String)
        periodo = db.Column(db.String)
        categoria_afetada = db.Column(db.String)


    class FeriadosDoAno(db.Model):
        __tablename__ = 'vw_feriados_do_ano'
        __table_args__ = {'info': {'is_view': True}}
        
        id_evento = db.Column(db.Integer, primary_key=True)
        feriado = db.Column(db.String)
        datainicio = db.Column(db.Date)
        datafim = db.Column(db.Date)
        calendario = db.Column(db.String)


    class DiasLetivosPorPeriodo(db.Model):
        __tablename__ = 'vw_dias_letivos_por_periodo'
        __table_args__ = {'info': {'is_view': True}}
        
        periodo = db.Column(db.String, primary_key=True)
        total_dias_letivos = db.Column(db.Integer)