from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
from app.models.models import Eventos, CategoriaCalendario, Calendario
from app.forms import EventoForm
from sqlalchemy import or_, and_

evento_bp = Blueprint('evento', __name__, url_prefix='/eventos')

@evento_bp.route('/')
def listar():
    eventos = Eventos.query.all()
    return render_template('eventos/listar.html', eventos=eventos)

@evento_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    form = EventoForm()
    form.id_categoria.choices = [(c.id_categoria, f"{c.nome} - {c.calendario.nome}") 
                                for c in CategoriaCalendario.query.all()]
    
    if form.validate_on_submit():
        evento = Eventos(
            id_categoria=form.id_categoria.data,
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            datainicio=form.datainicio.data,
            datafim=form.datafim.data,
            dia_todo=form.dia_todo.data,
            local=form.local.data
        )
        
        # Verificar conflitos de eventos
        conflitos = verificar_conflitos(evento)
        if conflitos:
            flash(f'Atenção! Existem {len(conflitos)} eventos conflitantes no mesmo período.', 'warning')
        
        db.session.add(evento)
        db.session.commit()
        flash('Evento criado com sucesso!', 'success')
        return redirect(url_for('evento.listar'))
        
    return render_template('eventos/form.html', form=form, titulo='Novo Evento')

@evento_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    evento = Eventos.query.get_or_404(id)
    form = EventoForm(obj=evento)
    form.id_categoria.choices = [(c.id_categoria, f"{c.nome} - {c.calendario.nome}") 
                                for c in CategoriaCalendario.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(evento)
        
        # Verificar conflitos de eventos
        conflitos = verificar_conflitos(evento, evento.id_evento)
        if conflitos:
            flash(f'Atenção! Existem {len(conflitos)} eventos conflitantes no mesmo período.', 'warning')
        
        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('evento.listar'))
        
    return render_template('eventos/form.html', form=form, titulo='Editar Evento')

@evento_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    evento = Eventos.query.get_or_404(id)
    
    db.session.delete(evento)
    db.session.commit()
    flash('Evento excluído com sucesso!', 'success')
    
    return redirect(url_for('evento.listar'))

@evento_bp.route('/calendario/<int:id>')
def eventos_calendario(id):
    calendario = Calendario.query.get_or_404(id)
    categorias = CategoriaCalendario.query.filter_by(id_calendario=id).all()
    categoria_ids = [c.id_categoria for c in categorias]
    
    eventos = Eventos.query.filter(Eventos.id_categoria.in_(categoria_ids)).all()
    
    # Formatar eventos para o fullCalendar
    eventos_formatados = []
    for evento in eventos:
        eventos_formatados.append({
            'id': evento.id_evento,
            'title': evento.titulo,
            'start': evento.datainicio.isoformat(),
            'end': evento.datafim.isoformat(),
            'allDay': evento.dia_todo,
            'color': evento.categoria.corassociada,
            'description': evento.descricao or '',
            'location': evento.local or ''
        })
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(eventos_formatados)
    
    return render_template('eventos/calendario.html', 
                           calendario=calendario, 
                           eventos=eventos_formatados)

def verificar_conflitos(evento, evento_id=None):
    """Verifica se há conflitos com outros eventos na mesma categoria e período"""
    query = Eventos.query.filter(
        Eventos.id_categoria == evento.id_categoria,
        and_(
            Eventos.datainicio <= evento.datafim,
            Eventos.datafim >= evento.datainicio
        )
    )
    
    if evento_id:
        query = query.filter(Eventos.id_evento != evento_id)
        
    return query.all()