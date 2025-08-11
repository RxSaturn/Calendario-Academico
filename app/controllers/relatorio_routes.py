from flask import Blueprint, render_template, jsonify, flash, redirect, url_for
from sqlalchemy import text, inspect
from app import db
from app.models.models import Periodo, Calendario, CategoriaCalendario
from datetime import date

# Verificamos se estamos usando PostgreSQL ou SQLite
def is_postgres():
    """Verifica se o banco de dados é PostgreSQL"""
    return db.engine.name == 'postgresql'

# Definimos um dicionário para armazenar modelos disponíveis
available_models = {}

# Importações condicionais para os modelos de visão
try:
    from app.models.views import (
        EventosAtivosHoje, ResumoCalendario, EventosFuturosAtivos, 
        is_sqlite
    )
    
    # Registramos os modelos básicos
    available_models['eventos_ativos'] = EventosAtivosHoje
    available_models['resumo_calendario'] = ResumoCalendario
    available_models['eventos_futuros'] = EventosFuturosAtivos
    
    # Importações condicionais para classes que só existem no PostgreSQL
    if not is_sqlite():
        from app.models.views import (
            DiasLetivos, FeriadosDiasLetivos, FeriadosDoAno, DiasLetivosPorPeriodo
        )
        
        # Registramos modelos específicos do PostgreSQL
        available_models['dias_letivos'] = DiasLetivos
        available_models['feriados_dias_letivos'] = FeriadosDiasLetivos
        available_models['feriados_ano'] = FeriadosDoAno
        available_models['dias_por_periodo'] = DiasLetivosPorPeriodo
except ImportError as e:
    print(f"Aviso: Alguns modelos de visão não puderam ser importados: {e}")

relatorio_bp = Blueprint('relatorio', __name__, url_prefix='/relatorios')

def view_exists(view_name):
    """Verifica se uma visão existe no banco de dados"""
    try:
        inspector = inspect(db.engine)
        return view_name in inspector.get_view_names()
    except:
        return False

@relatorio_bp.route('/')
def index():
    """Página principal de relatórios"""
    # Determinar quais relatórios estão disponíveis
    is_postgres_db = is_postgres()
    views_disponiveis = {
        'eventos_ativos': 'eventos_ativos' in available_models,
        'dias_letivos': 'dias_letivos' in available_models,
        'resumo_calendarios': 'resumo_calendario' in available_models,
        'feriados_dias_letivos': 'feriados_dias_letivos' in available_models,
        'eventos_futuros': 'eventos_futuros' in available_models,
        'feriados_ano': 'feriados_ano' in available_models,
        'dias_por_periodo': 'dias_por_periodo' in available_models
    }
    
    if not is_postgres_db:
        flash("Você está usando SQLite, que tem suporte limitado para visões avançadas. Para todas as funcionalidades, use PostgreSQL.", "warning")
    
    return render_template('relatorios/index.html', 
                           views_disponiveis=views_disponiveis,
                           is_postgres=is_postgres_db)

@relatorio_bp.route('/eventos-ativos')
def eventos_ativos():
    """Eventos ativos no período atual"""
    if 'eventos_ativos' not in available_models:
        flash("Esta visão não está disponível. Execute 'flask init-advanced-features' para criar as visões.", "danger")
        return redirect(url_for('relatorio.index'))
        
    try:
        eventos = available_models['eventos_ativos'].query.all()
        return render_template('relatorios/eventos_ativos.html', eventos=eventos)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/dias-letivos')
def dias_letivos():
    """Relatório de dias letivos"""
    if 'dias_letivos' not in available_models:
        flash("Esta visão não está disponível no SQLite. Para usar este relatório, configure um banco de dados PostgreSQL.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        dados = available_models['dias_letivos'].query.all()
        return render_template('relatorios/dias_letivos.html', dados=dados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/resumo-calendarios')
def resumo_calendarios():
    """Resumo de todos os calendários"""
    if 'resumo_calendario' not in available_models:
        flash("Esta visão não está disponível. Execute 'flask init-advanced-features' para criar as visões.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        dados = available_models['resumo_calendario'].query.all()
        return render_template('relatorios/resumo_calendarios.html', dados=dados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/feriados-dias-letivos')
def feriados_dias_letivos():
    """Feriados que caem em dias letivos"""
    if 'feriados_dias_letivos' not in available_models:
        flash("Esta visão não está disponível no SQLite. Para usar este relatório, configure um banco de dados PostgreSQL.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        dados = available_models['feriados_dias_letivos'].query.all()
        return render_template('relatorios/feriados_dias_letivos.html', dados=dados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/eventos-futuros')
def eventos_futuros():
    """Eventos futuros de calendários ativos"""
    if 'eventos_futuros' not in available_models:
        flash("Esta visão não está disponível. Execute 'flask init-advanced-features' para criar as visões.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        eventos = available_models['eventos_futuros'].query.all()
        return render_template('relatorios/eventos_futuros.html', eventos=eventos)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/feriados-ano')
def feriados_ano():
    """Feriados do ano atual"""
    if 'feriados_ano' not in available_models:
        flash("Esta visão não está disponível no SQLite. Para usar este relatório, configure um banco de dados PostgreSQL.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        feriados = available_models['feriados_ano'].query.all()
        return render_template('relatorios/feriados_ano.html', feriados=feriados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/dias-por-periodo')
def dias_por_periodo():
    """Contagem de dias letivos por período"""
    if 'dias_por_periodo' not in available_models:
        flash("Esta visão não está disponível no SQLite. Para usar este relatório, configure um banco de dados PostgreSQL.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        dados = available_models['dias_por_periodo'].query.all()
        return render_template('relatorios/dias_por_periodo.html', dados=dados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/utilizacao-funcao/<int:id_periodo>')
def utilizacao_funcao(id_periodo):
    """Exemplo de utilização direta de uma função PostgreSQL"""
    # Verificar se estamos usando PostgreSQL
    if not is_postgres():
        return jsonify({
            "erro": "Esta função requer PostgreSQL",
            "id_periodo": id_periodo,
            "duracao_dias": None
        })
    
    try:
        resultado = db.session.execute(
            text("SELECT calcular_duracao_periodo(:id)"), 
            {"id": id_periodo}
        ).scalar()
        
        return jsonify({
            "id_periodo": id_periodo,
            "duracao_dias": resultado
        })
    except Exception as e:
        return jsonify({
            "erro": str(e),
            "id_periodo": id_periodo,
            "duracao_dias": None
        })

@relatorio_bp.route('/total-eventos/<int:id_categoria>')
def total_eventos(id_categoria):
    """Contagem de eventos usando função PostgreSQL"""
    # Verificar se estamos usando PostgreSQL
    if not is_postgres():
        # Implementar alternativa em Python para SQLite
        from sqlalchemy import func
        from app.models.models import Eventos
        total = db.session.query(func.count()).filter_by(id_categoria=id_categoria).scalar()
        
        return jsonify({
            "nota": "Usando contagem via SQLAlchemy (sem função PostgreSQL)",
            "id_categoria": id_categoria,
            "total_eventos": total or 0
        })
    
    try:
        resultado = db.session.execute(
            text("SELECT contar_eventos_por_categoria(:id)"), 
            {"id": id_categoria}
        ).scalar()
        
        return jsonify({
            "id_categoria": id_categoria,
            "total_eventos": resultado
        })
    except Exception as e:
        return jsonify({
            "erro": str(e),
            "id_categoria": id_categoria,
            "total_eventos": None
        })

@relatorio_bp.route('/status-calendario/<int:id_calendario>')
def status_calendario(id_calendario):
    """Verifica se um calendário está ativo"""
    # Verificar se estamos usando PostgreSQL
    if not is_postgres():
        # Implementar alternativa em Python para SQLite
        calendario = Calendario.query.get_or_404(id_calendario)
        esta_ativo = (calendario.ativo and 
                      date.today() >= calendario.datainicio and 
                      date.today() <= calendario.datafim)
        
        return jsonify({
            "nota": "Usando verificação via Python (sem função PostgreSQL)",
            "id_calendario": id_calendario,
            "esta_ativo": esta_ativo
        })
    
    try:
        resultado = db.session.execute(
            text("SELECT esta_calendario_ativo(:id)"), 
            {"id": id_calendario}
        ).scalar()
        
        return jsonify({
            "id_calendario": id_calendario,
            "esta_ativo": resultado
        })
    except Exception as e:
        return jsonify({
            "erro": str(e),
            "id_calendario": id_calendario,
            "esta_ativo": None
        })

# Rota alternativa para SQLite que implementa consulta de eventos ativos diretamente
@relatorio_bp.route('/eventos-ativos-alternativo')
def eventos_ativos_alternativo():
    """Implementação alternativa de eventos ativos para SQLite"""
    from datetime import date
    from app.models.models import Eventos
    
    # Consulta equivalente usando SQLAlchemy
    eventos = (db.session.query(Eventos)
               .join(CategoriaCalendario, Eventos.id_categoria == CategoriaCalendario.id_categoria)
               .join(Calendario, CategoriaCalendario.id_calendario == Calendario.id_calendario)
               .join(Periodo, CategoriaCalendario.id_periodo == Periodo.id_periodo)
               .filter(Calendario.ativo == True)
               .filter(date.today() >= Periodo.datainicial)
               .filter(date.today() <= Periodo.datafinal)
               .filter(Eventos.datainicio >= date.today())
               .order_by(Eventos.datainicio)
               .all())
    
    return render_template('relatorios/eventos_ativos_alternativo.html', eventos=eventos)