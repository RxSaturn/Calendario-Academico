from flask import Blueprint, render_template
from app.models.models import Calendario, Eventos
from sqlalchemy import extract
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Obtém o ano atual
    ano_atual = datetime.now().year
    
    # Busca calendários ativos para o ano atual
    calendarios = Calendario.query.filter_by(ano=ano_atual, ativo=True).all()
    
    # Busca eventos próximos (próximos 15 dias)
    hoje = datetime.now().date()
    eventos_proximos = Eventos.query.filter(
        Eventos.datainicio >= hoje
    ).order_by(Eventos.datainicio).limit(10).all()
    
    return render_template('index.html', 
                           calendarios=calendarios,
                           eventos_proximos=eventos_proximos)

@main.route('/sobre')
def sobre():
    return render_template('sobre.html')