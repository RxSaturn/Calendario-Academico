from flask import Blueprint, render_template, jsonify, flash, redirect, url_for
from sqlalchemy import text, inspect
from app import db
from app.models.models import Periodo, Calendario, CategoriaCalendario

# Importações condicionais para lidar com diferentes tipos de banco de dados
try:
    from app.models.views import (
        EventosAtivosHoje, ResumoCalendario, EventosFuturosAtivos, 
        is_sqlite
    )
    # Importações condicionais para classes que só existem no PostgreSQL
    if not is_sqlite():
        from app.models.views import (
            DiasLetivos, FeriadosDiasLetivos, FeriadosDoAno, DiasLetivosPorPeriodo
        )
except ImportError:
    pass  # As classes não estão disponíveis

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
    is_postgres = db.engine.name == 'postgresql'
    views_disponiveis = {
        'eventos_ativos': view_exists('vw_eventos_ativos_hoje'),
        'dias_letivos': view_exists('vw_dias_letivos'),
        'resumo_calendarios': view_exists('vw_resumo_calendario'),
        'feriados_dias_letivos': view_exists('vw_feriados_dias_letivos'),
        'eventos_futuros': view_exists('vw_eventos_futuros_ativos'),
        'feriados_ano': view_exists('vw_feriados_do_ano'),
        'dias_por_periodo': view_exists('vw_dias_letivos_por_periodo')
    }
    
    if not is_postgres:
        flash("Você está usando SQLite, que tem suporte limitado para visões avançadas. Para todas as funcionalidades, use PostgreSQL.", "warning")
    
    return render_template('relatorios/index.html', 
                           views_disponiveis=views_disponiveis,
                           is_postgres=is_postgres)

@relatorio_bp.route('/eventos-ativos')
def eventos_ativos():
    """Eventos ativos no período atual"""
    if not view_exists('vw_eventos_ativos_hoje'):
        flash("Esta visão não está disponível. Execute 'flask init-advanced-features' para criar as visões.", "danger")
        return redirect(url_for('relatorio.index'))
        
    eventos = EventosAtivosHoje.query.all()
    return render_template('relatorios/eventos_ativos.html', eventos=eventos)

@relatorio_bp.route('/dias-letivos')
def dias_letivos():
    """Relatório de dias letivos"""
    if not view_exists('vw_dias_letivos'):
        flash("Esta visão não está disponível no SQLite. Para usar este relatório, configure um banco de dados PostgreSQL.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        dados = DiasLetivos.query.all()
        return render_template('relatorios/dias_letivos.html', dados=dados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/resumo-calendarios')
def resumo_calendarios():
    """Resumo de todos os calendários"""
    if not view_exists('vw_resumo_calendario'):
        flash("Esta visão não está disponível. Execute 'flask init-advanced-features' para criar as visões.", "danger")
        return redirect(url_for('relatorio.index'))
    
    dados = ResumoCalendario.query.all()
    return render_template('relatorios/resumo_calendarios.html', dados=dados)

@relatorio_bp.route('/feriados-dias-letivos')
def feriados_dias_letivos():
    """Feriados que caem em dias letivos"""
    if not view_exists('vw_feriados_dias_letivos'):
        flash("Esta visão não está disponível no SQLite. Para usar este relatório, configure um banco de dados PostgreSQL.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        dados = FeriadosDiasLetivos.query.all()
        return render_template('relatorios/feriados_dias_letivos.html', dados=dados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/eventos-futuros')
def eventos_futuros():
    """Eventos futuros de calendários ativos"""
    if not view_exists('vw_eventos_futuros_ativos'):
        flash("Esta visão não está disponível. Execute 'flask init-advanced-features' para criar as visões.", "danger")
        return redirect(url_for('relatorio.index'))
    
    eventos = EventosFuturosAtivos.query.all()
    return render_template('relatorios/eventos_futuros.html', eventos=eventos)

@relatorio_bp.route('/feriados-ano')
def feriados_ano():
    """Feriados do ano atual"""
    if not view_exists('vw_feriados_do_ano'):
        flash("Esta visão não está disponível no SQLite. Para usar este relatório, configure um banco de dados PostgreSQL.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        feriados = FeriadosDoAno.query.all()
        return render_template('relatorios/feriados_ano.html', feriados=feriados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/dias-por-periodo')
def dias_por_periodo():
    """Contagem de dias letivos por período"""
    if not view_exists('vw_dias_letivos_por_periodo'):
        flash("Esta visão não está disponível no SQLite. Para usar este relatório, configure um banco de dados PostgreSQL.", "danger")
        return redirect(url_for('relatorio.index'))
    
    try:
        dados = DiasLetivosPorPeriodo.query.all()
        return render_template('relatorios/dias_por_periodo.html', dados=dados)
    except Exception as e:
        flash(f"Erro ao acessar a visão: {str(e)}", "danger")
        return redirect(url_for('relatorio.index'))

@relatorio_bp.route('/utilizacao-funcao/<int:id_periodo>')
def utilizacao_funcao(id_periodo):
    """Exemplo de utilização direta de uma função PostgreSQL"""
    # Verificar se estamos usando PostgreSQL
    if db.engine.name != 'postgresql':
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
    if db.engine.name != 'postgresql':
        # Implementar alternativa em Python para SQLite
        from sqlalchemy import func
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
    if db.engine.name != 'postgresql':
        # Implementar alternativa em Python para SQLite
        calendario = Calendario.query.get_or_404(id_calendario)
        from datetime import date
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