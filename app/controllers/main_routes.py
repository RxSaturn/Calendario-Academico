from flask import Blueprint, render_template, flash
from app.models.models import Calendario, Eventos
from sqlalchemy import extract, desc
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Buscar o ano atual
    ano_atual = datetime.now().year
    
    # Buscar calendários ativos
    calendarios_ativos = Calendario.query.filter_by(ativo=True).all()
    
    # Se não houver calendários ativos, exibir uma mensagem
    if not calendarios_ativos:
        flash('Não há calendários ativos no sistema. Por favor, ative algum calendário.', 'info')
    
    # Contar eventos por calendário
    contagem_eventos = {}
    for calendario in calendarios_ativos:
        # Contar eventos em todas as categorias do calendário
        evento_ids = []
        for categoria in calendario.categorias:
            for evento in categoria.eventos:
                evento_ids.append(evento.id_evento)
        
        contagem_eventos[calendario.id_calendario] = len(set(evento_ids))
    
    # Estatísticas gerais
    total_eventos = Eventos.query.count()
    
    # Eventos recentes
    eventos_recentes = (Eventos.query
                        .order_by(desc(Eventos.datainicio))
                        .limit(5)
                        .all())
    
    # Busca eventos próximos (próximos 15 dias)
    hoje = datetime.now().date()
    eventos_proximos = Eventos.query.filter(
        Eventos.datainicio >= hoje
    ).order_by(Eventos.datainicio).limit(10).all()
    
    return render_template('index.html', 
                          calendarios_ativos=calendarios_ativos,
                          contagem_eventos=contagem_eventos,
                          total_eventos=total_eventos,
                          eventos_recentes=eventos_recentes,
                          eventos_proximos=eventos_proximos,
                          ano_atual=ano_atual)

@main.route('/sobre')
def sobre():
    return render_template('sobre.html')