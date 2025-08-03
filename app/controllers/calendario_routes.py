from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models.models import Calendario, TipoCalendario
from app.forms import CalendarioForm

calendario_bp = Blueprint('calendario', __name__, url_prefix='/calendarios')

@calendario_bp.route('/')
def listar():
    calendarios = Calendario.query.all()
    return render_template('calendarios/listar.html', calendarios=calendarios)

@calendario_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    form = CalendarioForm()
    # Carrega os tipos de calendário para o dropdown
    form.id_tipo.choices = [(t.id_tipo, f"{t.sigla} - {t.nome}") for t in TipoCalendario.query.all()]
    
    if form.validate_on_submit():
        calendario = Calendario(
            id_tipo=form.id_tipo.data,
            nome=form.nome.data,
            ano=form.ano.data,
            datainicio=form.datainicio.data,
            datafim=form.datafim.data,
            ativo=form.ativo.data
        )
        
        db.session.add(calendario)
        db.session.commit()
        flash('Calendário criado com sucesso!', 'success')
        return redirect(url_for('calendario.listar'))
        
    return render_template('calendarios/form.html', form=form, titulo='Novo Calendário')

@calendario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    calendario = Calendario.query.get_or_404(id)
    form = CalendarioForm(obj=calendario)
    form.id_tipo.choices = [(t.id_tipo, f"{t.sigla} - {t.nome}") for t in TipoCalendario.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(calendario)
        db.session.commit()
        flash('Calendário atualizado com sucesso!', 'success')
        return redirect(url_for('calendario.listar'))
        
    return render_template('calendarios/form.html', form=form, titulo='Editar Calendário')

@calendario_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    calendario = Calendario.query.get_or_404(id)
    
    try:
        db.session.delete(calendario)
        db.session.commit()
        flash('Calendário excluído com sucesso!', 'success')
    except Exception:
        db.session.rollback()
        flash('Não foi possível excluir este calendário. Verifique se há categorias associadas.', 'danger')
    
    return redirect(url_for('calendario.listar'))

@calendario_bp.route('/visualizar/<int:id>')
def visualizar(id):
    calendario = Calendario.query.get_or_404(id)
    return render_template('calendarios/visualizar.html', calendario=calendario)